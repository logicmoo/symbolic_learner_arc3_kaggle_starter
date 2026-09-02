"""A shared, long-lived background job system for the workbench backend.

Any subsystem can hand a job to the singleton manager and get back a job
record it can poll for status. Jobs run in a process pool so CPU-bound work
(such as rebuilding the resource AtomSpace over thousands of JSON resources)
uses multiple cores instead of contending on the GIL, and never blocks the
web request that scheduled it.

Because jobs run in separate processes, the job callable and its arguments
must be importable/picklable: pass a top-level function plus simple argument
values, have the function do its own I/O (e.g. write results to disk), and
return only a small, picklable summary. If a process pool cannot be created
in the current environment, the manager transparently falls back to a thread
pool so scheduling still works (without true multi-core parallelism).
"""

from __future__ import annotations

import os
import time
import uuid
import atexit
import threading
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Optional

_MAX_WORKERS = max(1, int(os.environ.get("WORKBENCH_JOB_WORKERS", str(min(4, (os.cpu_count() or 2))))))
_HISTORY_LIMIT = max(50, int(os.environ.get("WORKBENCH_JOB_HISTORY", "200")))

_ACTIVE_STATUSES = ("queued", "running")


class Job:
    """A single unit of background work and its observable status."""

    def __init__(self, kind: str, title: Optional[str], key: Optional[str], metadata: Optional[dict[str, Any]]):
        self.id = uuid.uuid4().hex
        self.kind = kind
        self.title = title or kind
        self.key = key
        self.metadata: dict[str, Any] = dict(metadata or {})
        self.status = "queued"
        self.executor: Optional[str] = None
        self.error: Optional[str] = None
        self.result: Optional[dict[str, Any]] = None
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.cancel_requested = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "key": self.key,
            "status": self.status,
            "executor": self.executor,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at,
            "cancelRequested": self.cancel_requested,
            "durationMs": (
                round(((self.finished_at or time.time()) - self.started_at) * 1000)
                if self.started_at
                else None
            ),
        }


class JobManager:
    """Owns the process pool and the registry of submitted jobs."""

    def __init__(self, max_workers: int):
        self._max_workers = max_workers
        self._lock = threading.RLock()
        self._jobs: dict[str, Job] = {}
        self._by_key: dict[str, str] = {}
        self._futures: dict[str, Future] = {}
        # Two long-lived pools, created lazily and selectable per job:
        #   "process" -> ProcessPoolExecutor (true multi-core, CPU-bound work)
        #   "thread"  -> ThreadPoolExecutor  (I/O-bound work, orchestration)
        self._pools: dict[str, Any] = {}
        self._atexit_registered = False

    def _ensure_pool(self, kind: str) -> tuple[Any, str]:
        """Return (pool, actual_kind); falls back to a thread pool if a process
        pool cannot be created in this environment."""
        if kind not in ("process", "thread"):
            kind = "process"
        with self._lock:
            pool = self._pools.get(kind)
            if pool is not None:
                return pool, kind
            actual = kind
            try:
                if kind == "process":
                    pool = ProcessPoolExecutor(max_workers=self._max_workers)
                else:
                    pool = ThreadPoolExecutor(
                        max_workers=self._max_workers, thread_name_prefix="workbench-job"
                    )
            except Exception:  # noqa: BLE001 - restricted envs cannot spawn processes
                actual = "thread"
                pool = self._pools.get("thread")
                if pool is None:
                    pool = ThreadPoolExecutor(
                        max_workers=self._max_workers, thread_name_prefix="workbench-job"
                    )
                    self._pools["thread"] = pool
            self._pools[actual] = pool
            if not self._atexit_registered:
                atexit.register(self.shutdown)
                self._atexit_registered = True
            return pool, actual

    @property
    def pool_kinds(self) -> list[str]:
        with self._lock:
            return sorted(self._pools.keys())

    def submit(
        self,
        fn: Callable[..., dict[str, Any] | None],
        args: tuple[Any, ...] = (),
        *,
        kind: str,
        title: Optional[str] = None,
        key: Optional[str] = None,
        dedupe: bool = True,
        executor: str = "process",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Job:
        """Schedule ``fn(*args)`` on the chosen pool and return its Job record.

        ``executor`` selects the pool: ``"process"`` for CPU-bound work (true
        multi-core) or ``"thread"`` for I/O-bound work and orchestration. When
        ``dedupe`` is set and a job with the same ``key`` is still active, that
        existing job is returned instead of scheduling a duplicate.
        """
        with self._lock:
            if dedupe and key is not None:
                existing_id = self._by_key.get(key)
                if existing_id:
                    existing = self._jobs.get(existing_id)
                    if existing and existing.status in _ACTIVE_STATUSES:
                        return existing
            job = Job(kind, title, key, metadata)
            self._jobs[job.id] = job
            if key is not None:
                self._by_key[key] = job.id
            self._prune_locked()

        pool, actual_kind = self._ensure_pool(executor)
        job.executor = actual_kind
        job.status = "running"
        job.started_at = time.time()
        try:
            future = pool.submit(fn, *args)
        except Exception as error:  # noqa: BLE001 - pool refused the work
            job.status = "failed"
            job.error = f"could not schedule job: {error}"
            job.finished_at = time.time()
            return job

        with self._lock:
            self._futures[job.id] = future
        future.add_done_callback(lambda completed, job_id=job.id: self._on_done(job_id, completed))
        return job

    def _on_done(self, job_id: str, future: Future) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            self._futures.pop(job_id, None)
        if job is None:
            return
        job.finished_at = time.time()
        if future.cancelled():
            job.status = "cancelled"
            return
        error = future.exception()
        if error is not None:
            job.status = "failed"
            job.error = str(error)
            return
        result = future.result()
        job.status = "succeeded"
        if isinstance(result, dict):
            job.result = result

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def by_key(self, key: str) -> Optional[Job]:
        with self._lock:
            job_id = self._by_key.get(key)
            return self._jobs.get(job_id) if job_id else None

    def list(self, kind: Optional[str] = None, limit: Optional[int] = None) -> list[Job]:
        with self._lock:
            jobs = [job for job in self._jobs.values() if kind is None or job.kind == kind]
        jobs.sort(key=lambda job: job.created_at, reverse=True)
        return jobs[:limit] if limit else jobs

    def cancel(self, job_id: str) -> Optional[Job]:
        with self._lock:
            job = self._jobs.get(job_id)
            future = self._futures.get(job_id)
        if job is None:
            return None
        job.cancel_requested = True
        if future is not None and future.cancel():
            job.status = "cancelled"
            job.finished_at = time.time()
        return job

    def _prune_locked(self) -> None:
        if len(self._jobs) <= _HISTORY_LIMIT:
            return
        finished = sorted(
            (job for job in self._jobs.values() if job.status not in _ACTIVE_STATUSES),
            key=lambda job: job.finished_at or job.created_at,
        )
        for job in finished[: len(self._jobs) - _HISTORY_LIMIT]:
            self._jobs.pop(job.id, None)
            if job.key and self._by_key.get(job.key) == job.id:
                self._by_key.pop(job.key, None)

    def shutdown(self) -> None:
        with self._lock:
            pools = list(self._pools.values())
            self._pools = {}
        for pool in pools:
            try:
                pool.shutdown(wait=False, cancel_futures=True)
            except TypeError:
                pool.shutdown(wait=False)


_manager: Optional[JobManager] = None
_manager_lock = threading.Lock()


def get_job_manager() -> JobManager:
    """Return the process-wide singleton job manager, creating it on first use."""
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = JobManager(_MAX_WORKERS)
    return _manager
