"""HTTP surface for the shared background job system (see job_manager.py)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from job_manager import get_job_manager

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(kind: Optional[str] = None, limit: Optional[int] = None) -> dict[str, Any]:
    manager = get_job_manager()
    return {
        "poolKinds": manager.pool_kinds,
        "jobs": [job.to_dict() for job in manager.list(kind=kind, limit=limit)],
    }


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = get_job_manager().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job.to_dict()


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    job = get_job_manager().cancel(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job.to_dict()
