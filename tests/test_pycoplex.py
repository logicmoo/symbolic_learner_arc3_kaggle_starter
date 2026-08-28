from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx
import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PACKAGES = REPOSITORY_ROOT / "workbench" / "plugins"
if str(PLUGIN_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PLUGIN_PACKAGES))

import pycoplex.runtime as harness_module
from pycoplex import HarnessTaskManager, LLMTaskHarness, OpenAICompatibleAdapter


def final(text: str = "done") -> dict[str, object]:
    return {"content": text, "tool_calls": []}


def call(name: str, arguments: dict[str, object] | None = None, call_id: str = "call-1") -> dict[str, object]:
    return {
        "content": "working",
        "tool_calls": [{"id": call_id, "name": name, "arguments": arguments or {}}],
    }


def scripted(*replies: dict[str, object]):
    lock = threading.Lock()
    items = iter(replies)
    requests: list[dict[str, object]] = []

    def adapter(request: dict[str, object]) -> dict[str, object]:
        with lock:
            requests.append(request)
            return next(items)

    adapter.requests = requests
    return adapter


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello harness\n", encoding="utf-8")
    return tmp_path


def wait_for(manager: HarnessTaskManager, task_id: str, states: set[str], timeout: float = 5) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        task = manager.get(task_id)
        if task["status"] in states:
            return task
        time.sleep(0.01)
    raise AssertionError(f"task never reached {states}: {manager.get(task_id)}")


def test_tool_round_trip_and_repository_context(repository: Path) -> None:
    adapter = scripted(call("read_file", {"path": "README.md"}), final("inspected"))
    with LLMTaskHarness(adapter, repository) as harness:
        assert harness.run("inspect") == "inspected"
    tool_message = adapter.requests[1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert tool_message["content"]["ok"] is True
    assert "hello harness" in tool_message["content"]["content"]
    assert "Repository root:" in adapter.requests[0]["messages"][0]["content"]


def test_scoped_atomic_write_preserves_mode_and_rejects_escape(repository: Path) -> None:
    target = repository / "executable.py"
    target.write_text("print('old')\n", encoding="utf-8")
    target.chmod(0o755)
    previous_mode = target.stat().st_mode
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
    ) as harness:
        written = harness.execute_tool("write_file", {"path": "executable.py", "content": "print('new')\n"})
        escaped = harness.execute_tool("write_file", {"path": "../escape.txt", "content": "no"})
        denied = harness.execute_tool("read_file", {"path": ".env"})
    assert written["ok"] is True
    assert target.read_text(encoding="utf-8") == "print('new')\n"
    assert target.stat().st_mode == previous_mode
    assert escaped["ok"] is False
    assert denied["ok"] is False


def test_cancelled_harness_rejects_late_mutating_tools(repository: Path) -> None:
    harness = LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
    )
    harness.cancel()
    try:
        with pytest.raises(RuntimeError, match="cancelled"):
            harness.execute_tool("write_file", {"path": "late.txt", "content": "no"})
        with pytest.raises(RuntimeError, match="cancelled"):
            harness.execute_tool("make_directory", {"path": "late-directory"})
    finally:
        harness.close()
    assert not (repository / "late.txt").exists()
    assert not (repository / "late-directory").exists()


def test_cancellation_during_approval_fences_tool_dispatch(repository: Path) -> None:
    harness: LLMTaskHarness

    def approval(*_: object) -> bool:
        harness.cancel()
        return True

    harness = LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
        approval=approval,
    )
    try:
        with pytest.raises(RuntimeError, match="cancelled"):
            harness.execute_tool("write_file", {"path": "approval-race.txt", "content": "no"})
    finally:
        harness.close()
    assert not (repository / "approval-race.txt").exists()


def test_root_level_and_case_variant_secret_files_are_denied(repository: Path) -> None:
    names = (
        "root.pem", "ROOT.PEM", ".CREDENTIALS", "id_rsa",
        ".env.local", ".ENV.PRODUCTION", "nested/.env.development",
    )
    for name in names:
        target = repository / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"secret-canary:{name}\n", encoding="utf-8")
    with LLMTaskHarness(scripted(final()), repository) as harness:
        reads = [harness.execute_tool("read_file", {"path": name}) for name in names]
        listing = harness.execute_tool("list_files", {"path": "."})
    assert all(result["ok"] is False for result in reads)
    assert listing["ok"] is True
    assert {path.casefold() for path in listing["files"]}.isdisjoint({
        "root.pem", ".credentials", "id_rsa", ".env.local",
        ".env.production", "nested/.env.development",
    })


def test_search_treats_leading_dash_query_as_data(repository: Path) -> None:
    (repository / "flags.txt").write_text("--pre=never-run\n", encoding="utf-8")
    (repository / "public.pem").write_text("denied-search-canary\n", encoding="utf-8")
    with LLMTaskHarness(scripted(final()), repository) as harness:
        result = harness.execute_tool("search", {"query": "--pre=never-run"})
        denied = harness.execute_tool("search", {"query": "denied-search-canary"})
    assert result["ok"] is True
    assert any("flags.txt" in match for match in result["matches"])
    assert denied["ok"] is True
    assert denied["matches"] == []


def test_search_fallback_is_fixed_text_and_skips_oversized_files(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (repository / "small.txt").write_text("Fallback Needle\n", encoding="utf-8")
    (repository / "large.txt").write_text("large-secret-canary" * 100, encoding="utf-8")
    (repository / "long-line.txt").write_text("output-needle-" + ("x" * 300), encoding="utf-8")
    monkeypatch.setattr(harness_module.shutil, "which", lambda _: None)
    with LLMTaskHarness(
        scripted(final()),
        repository,
        max_file_bytes=128,
    ) as harness:
        fixed = harness.execute_tool("search", {"query": "fallback needle"})
        regex = harness.execute_tool("search", {"query": "(a+)+$", "regex": True})
        large = harness.execute_tool("search", {"query": "large-secret-canary"})
    with LLMTaskHarness(
        scripted(final()),
        repository,
        max_file_bytes=1024,
        max_output_bytes=32,
    ) as harness:
        bounded = harness.execute_tool("search", {"query": "output-needle"})
    assert fixed["ok"] is True
    assert fixed["matches"] == ["small.txt:1:Fallback Needle"]
    assert regex["ok"] is False
    assert "requires ripgrep" in regex["error"]["message"]
    assert large["ok"] is True
    assert large["matches"] == []
    assert bounded["ok"] is True
    assert bounded["truncated"] is True
    assert sum(len(match.encode()) for match in bounded["matches"]) <= 32


def test_run_tests_cannot_bypass_command_policy(repository: Path) -> None:
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
        allow_shell=True,
    ) as harness:
        result = harness.execute_tool("run_tests", {"command": "git", "args": ["reset", "--hard"]})
    assert result["ok"] is False
    assert "mutating Git" in result["error"]["message"]


def test_apply_patch_rejects_quoted_denied_path(repository: Path) -> None:
    patch = """diff --git \"a/audit-denied.pem\" \"b/audit-denied.pem\"
new file mode 100644
--- /dev/null
+++ \"b/audit-denied.pem\"
@@ -0,0 +1 @@
+must-not-be-written
"""
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
    ) as harness:
        result = harness.execute_tool("apply_patch", {"patch": patch})
    assert result["ok"] is False
    assert "quoted or escaped" in result["error"]["message"]
    assert not (repository / "audit-denied.pem").exists()


def test_git_inspection_does_not_expose_denied_file_content(repository: Path) -> None:
    public = repository / "public.txt"
    denied = repository / "audit-denied.pem"
    public.write_text("public-before\n", encoding="utf-8")
    denied.write_text("denied-before\n", encoding="utf-8")
    subprocess.run(["git", "add", "public.txt", "audit-denied.pem"], cwd=repository, check=True)
    subprocess.run(
        [
            "git", "-c", "user.name=Harness Test", "-c", "user.email=harness@example.invalid",
            "commit", "-q", "-m", "fixture",
        ],
        cwd=repository,
        check=True,
    )
    public.write_text("public-after\n", encoding="utf-8")
    denied.write_text("denied-after-canary\n", encoding="utf-8")
    with LLMTaskHarness(scripted(final()), repository) as harness:
        diff = harness.execute_tool("git_diff", {})
        scoped_diff = harness.execute_tool("git_diff", {"path": "."})
        magic_diff = harness.execute_tool("git_diff", {"path": ":(top,glob)*"})
        blob = harness.execute_tool("git_show", {"object": "HEAD:audit-denied.pem"})
    assert diff["ok"] is True
    assert "public-after" in diff["stdout"]
    assert "denied-after-canary" not in diff["stdout"]
    assert scoped_diff["ok"] is True
    assert "public-after" in scoped_diff["stdout"]
    assert "denied-after-canary" not in scoped_diff["stdout"]
    assert "denied-after-canary" not in magic_diff.get("stdout", "")
    assert blob["ok"] is False


def test_configured_git_read_scope_is_always_a_literal_pathspec(repository: Path) -> None:
    public = repository / "public.txt"
    public.write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "add", "public.txt"], cwd=repository, check=True)
    subprocess.run(
        [
            "git", "-c", "user.name=Harness Test", "-c", "user.email=harness@example.invalid",
            "commit", "-q", "-m", "fixture",
        ],
        cwd=repository,
        check=True,
    )
    public.write_text("scope-escape-canary\n", encoding="utf-8")
    with LLMTaskHarness(
        scripted(final()),
        repository,
        readable_paths=(":(top,glob)*",),
    ) as harness:
        result = harness.execute_tool("git_diff", {})
    assert "scope-escape-canary" not in result.get("stdout", "")


def test_task_and_network_limits_are_enforced(repository: Path) -> None:
    with pytest.raises(ValueError, match="message limit"):
        with LLMTaskHarness(scripted(final()), repository, max_message_bytes=8) as harness:
            harness.run("this task is too long")
    with pytest.raises(ValueError, match="allowed_hosts"):
        LLMTaskHarness(scripted(final()), repository, allow_network=True)


def test_context_budget_rejects_oversized_mandatory_task_before_model_call(repository: Path) -> None:
    called = False

    def adapter(_: dict[str, object]) -> dict[str, object]:
        nonlocal called
        called = True
        return final()

    with LLMTaskHarness(
        adapter,
        repository,
        max_context_bytes=1024,
        max_message_bytes=4096,
    ) as harness:
        with pytest.raises(ValueError, match="mandatory repository context"):
            harness.run("x" * 900)
    assert called is False


def test_context_budget_never_silently_truncates_applicable_agents_instructions(repository: Path) -> None:
    (repository / "AGENTS.md").write_text(
        "instruction-padding\n" + ("x" * 2200) + "\nMUST-KEEP-TAIL\n",
        encoding="utf-8",
    )
    adapter = scripted(final("done"))
    with LLMTaskHarness(
        adapter,
        repository,
        max_context_bytes=4096,
        max_message_bytes=4096,
    ) as harness:
        assert harness.run("retain every applicable instruction") == "done"
    system_context = adapter.requests[0]["messages"][0]["content"]
    assert "instruction-padding" in system_context
    assert "MUST-KEEP-TAIL" in system_context


def test_repository_context_rejects_oversized_instruction_before_reading(repository: Path) -> None:
    (repository / "AGENTS.md").write_text("x" * 5000, encoding="utf-8")
    with LLMTaskHarness(
        scripted(final()),
        repository,
        max_context_bytes=1024,
    ) as harness:
        with pytest.raises(ValueError, match="instructions exceed"):
            harness.repository_context()


def test_repository_context_excludes_nested_instructions_outside_read_scope(repository: Path) -> None:
    (repository / "AGENTS.md").write_text("root-policy-canary\n", encoding="utf-8")
    allowed = repository / "python" / "package"
    allowed.mkdir(parents=True)
    (repository / "python" / "AGENTS.md").write_text("ancestor-policy-canary\n", encoding="utf-8")
    (allowed / "AGENTS.md").write_text("allowed-policy-canary\n", encoding="utf-8")
    excluded = repository / "workbench" / "private"
    excluded.mkdir(parents=True)
    (excluded / "AGENTS.md").write_text("excluded-policy-canary\n", encoding="utf-8")

    with LLMTaskHarness(
        scripted(final()),
        repository,
        readable_paths=("python/package",),
    ) as harness:
        context = harness.repository_context()

    assert "root-policy-canary" in context
    assert "ancestor-policy-canary" in context
    assert "allowed-policy-canary" in context
    assert "excluded-policy-canary" not in context


def test_startup_context_does_not_block_cancellation(repository: Path) -> None:
    entered = threading.Event()
    escape = threading.Event()
    harness = LLMTaskHarness(scripted(final()), repository, timeout=30)
    failures: list[BaseException] = []

    def blocking_context(*_: object, **__: object) -> str:
        entered.set()
        while not harness.cancelled and not escape.wait(0.01):
            pass
        return "context released"

    def run() -> None:
        try:
            harness.run("cancel during context")
        except BaseException as error:
            failures.append(error)

    harness.repository_context = blocking_context  # type: ignore[method-assign]
    run_thread = threading.Thread(
        target=run,
        name="startup-context-run-test",
    )
    cancel_thread = threading.Thread(target=harness.cancel, name="startup-context-cancel-test")
    run_thread.start()
    try:
        assert entered.wait(3)
        cancel_thread.start()
        cancel_thread.join(timeout=1)
        assert not cancel_thread.is_alive()
        run_thread.join(timeout=2)
        assert not run_thread.is_alive()
        assert failures and "cancelled" in str(failures[0])
    finally:
        escape.set()
        harness.cancel()
        cancel_thread.join(timeout=2)
        run_thread.join(timeout=2)
        harness.close()


def test_context_compaction_keeps_mandatory_pair_and_complete_latest_turn(repository: Path) -> None:
    (repository / "AGENTS.md").write_text("instruction-canary\n", encoding="utf-8")
    (repository / "first.txt").write_text("a" * 320, encoding="utf-8")
    (repository / "second.txt").write_text("b" * 320, encoding="utf-8")
    adapter = scripted(
        call("read_file", {"path": "first.txt"}, "first-call"),
        call("read_file", {"path": "second.txt"}, "second-call"),
        final("complete"),
    )
    with LLMTaskHarness(
        adapter,
        repository,
        max_context_bytes=1800,
        max_message_bytes=4096,
    ) as harness:
        assert harness.run("inspect both files") == "complete"
    request = adapter.requests[2]
    messages = request["messages"]
    assert len(json.dumps(messages, ensure_ascii=False).encode()) <= 1800
    assert messages[0] == adapter.requests[0]["messages"][0]
    assert messages[1] == {"role": "user", "content": "inspect both files"}
    assert "instruction-canary" in messages[0]["content"]
    tool_positions = [index for index, message in enumerate(messages) if message["role"] == "tool"]
    assert tool_positions
    for index in tool_positions:
        assistant = messages[index - 1]
        assert assistant["role"] == "assistant"
        assert any(call["id"] == messages[index]["tool_call_id"] for call in assistant["tool_calls"])
    assert messages[-1]["role"] == "tool"
    assert messages[-1]["tool_call_id"] == "second-call"


def test_guarded_http_pins_the_validated_public_address(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolutions = 0
    connected: list[str] = []

    def resolve(*_: object, **__: object) -> list[tuple[object, ...]]:
        nonlocal resolutions
        resolutions += 1
        address = "93.184.216.34" if resolutions == 1 else "127.0.0.1"
        return [(2, 1, 6, "", (address, 80))]

    class Headers(dict[str, str]):
        def get_content_charset(self) -> str:
            return "utf-8"

    class Response:
        status = 200
        headers = Headers({"Content-Type": "text/plain"})

        def __init__(self) -> None:
            self.sent = False

        def read(self, _: int = -1) -> bytes:
            if self.sent:
                return b""
            self.sent = True
            return b"pinned"

        def close(self) -> None:
            return None

    class Connection:
        def __init__(self, _: str, address: str, __: int, *, timeout: float) -> None:
            connected.append(address)

        def request(self, *_: object, **__: object) -> None:
            return None

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            return None

    monkeypatch.setattr(harness_module.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(harness_module, "_PinnedHTTPConnection", Connection)
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="full-access",
        allow_network=True,
        allowed_hosts=("example.com",),
    ) as harness:
        result = harness.execute_tool("web_get", {"url": "http://example.com/value"})
    assert result["ok"] is True
    assert result["content"] == "pinned"
    assert connected == ["93.184.216.34"]
    assert resolutions == 1


def test_guarded_http_cancellation_closes_blocking_response(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    read_started = threading.Event()
    response_closed = threading.Event()
    connection_closed = threading.Event()

    class Headers(dict[str, str]):
        def get_content_charset(self) -> str:
            return "utf-8"

    class BlockingResponse:
        status = 200
        headers = Headers({"Content-Type": "text/plain"})

        def read(self, _: int = -1) -> bytes:
            read_started.set()
            response_closed.wait(5)
            raise OSError("response closed")

        def close(self) -> None:
            response_closed.set()

    class BlockingConnection:
        def __init__(self, *_: object, **__: object) -> None:
            self.response = BlockingResponse()

        def request(self, *_: object, **__: object) -> None:
            return None

        def getresponse(self) -> BlockingResponse:
            return self.response

        def close(self) -> None:
            connection_closed.set()
            self.response.close()

    monkeypatch.setattr(
        harness_module.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("93.184.216.34", 80))],
    )
    monkeypatch.setattr(harness_module, "_PinnedHTTPConnection", BlockingConnection)
    harness = LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="full-access",
        allow_network=True,
        allowed_hosts=("example.com",),
    )
    results: list[dict[str, object]] = []
    thread = threading.Thread(
        target=lambda: results.append(harness.execute_tool("web_get", {"url": "http://example.com/value"})),
        name="guarded-http-cancel-test",
    )
    thread.start()
    try:
        assert read_started.wait(3)
        harness.cancel()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert response_closed.is_set()
        assert connection_closed.is_set()
        assert results and results[0]["ok"] is False
        assert "cancelled" in str(results[0]["error"])
        assert harness._network_resources == set()
    finally:
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


def test_guarded_http_cancel_before_request_aborts_without_dispatch(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tracked = threading.Event()
    release = threading.Event()
    socket_created = threading.Event()

    monkeypatch.setattr(
        harness_module.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("93.184.216.34", 80))],
    )
    monkeypatch.setattr(
        harness_module.socket,
        "create_connection",
        lambda *_args, **_kwargs: socket_created.set(),
    )
    harness = LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="full-access",
        allow_network=True,
        allowed_hosts=("example.com",),
    )
    original_track = harness._track_network_resource

    def paused_track(resource: object) -> None:
        original_track(resource)
        tracked.set()
        release.wait(5)

    harness._track_network_resource = paused_track  # type: ignore[method-assign]
    results: list[dict[str, object]] = []
    thread = threading.Thread(
        target=lambda: results.append(harness.execute_tool("web_get", {"url": "http://example.com/value"})),
        name="guarded-http-predispatch-cancel-test",
    )
    thread.start()
    try:
        assert tracked.wait(3)
        harness.cancel()
        release.set()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert not socket_created.is_set()
        assert results and results[0]["ok"] is False
    finally:
        release.set()
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


def test_pinned_connection_abort_during_connect_never_sends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connecting = threading.Event()
    release = threading.Event()
    socket_closed = threading.Event()
    sent = threading.Event()

    class FakeSocket:
        def close(self) -> None:
            socket_closed.set()

        def sendall(self, _: bytes) -> None:
            sent.set()

    def create_connection(*_: object, **__: object) -> FakeSocket:
        connecting.set()
        release.wait(5)
        return FakeSocket()

    monkeypatch.setattr(harness_module.socket, "create_connection", create_connection)
    connection = harness_module._PinnedHTTPConnection(
        "example.com", "93.184.216.34", 80, timeout=30
    )
    failures: list[BaseException] = []

    def request() -> None:
        try:
            connection.request("GET", "/")
        except BaseException as error:
            failures.append(error)

    thread = threading.Thread(target=request, name="pinned-connect-abort-test")
    thread.start()
    try:
        assert connecting.wait(3)
        connection.abort()
        release.set()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert socket_closed.is_set()
        assert not sent.is_set()
        assert failures and isinstance(failures[0], harness_module.http.client.CannotSendRequest)
    finally:
        release.set()
        connection.abort()
        thread.join(timeout=3)


def test_guarded_http_dns_resolution_is_cancellable(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolving = threading.Event()
    release = threading.Event()

    def blocked_resolution(*_: object, **__: object) -> list[tuple[object, ...]]:
        resolving.set()
        release.wait(5)
        return [(2, 1, 6, "", ("93.184.216.34", 80))]

    monkeypatch.setattr(harness_module.socket, "getaddrinfo", blocked_resolution)
    harness = LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="full-access",
        allow_network=True,
        allowed_hosts=("example.com",),
        timeout=30,
    )
    results: list[dict[str, object]] = []
    thread = threading.Thread(
        target=lambda: results.append(harness.execute_tool("web_get", {"url": "http://example.com/value"})),
        name="guarded-http-dns-cancel-test",
    )
    thread.start()
    try:
        assert resolving.wait(3)
        harness.cancel()
        thread.join(timeout=2)
        assert not thread.is_alive()
        assert results and results[0]["ok"] is False
        assert "cancelled" in str(results[0]["error"])
    finally:
        release.set()
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


def test_guarded_http_repeated_dns_cancellation_uses_bounded_workers(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    release = threading.Event()

    def blocked_resolution(*_: object, **__: object) -> list[tuple[object, ...]]:
        release.wait(5)
        return [(2, 1, 6, "", ("93.184.216.34", 80))]

    monkeypatch.setattr(harness_module.socket, "getaddrinfo", blocked_resolution)
    threads: list[threading.Thread] = []
    harnesses: list[LLMTaskHarness] = []
    try:
        for index in range(10):
            harness = LLMTaskHarness(
                scripted(final()),
                repository,
                permission_profile="full-access",
                allow_network=True,
                allowed_hosts=("example.com",),
                timeout=30,
            )
            harnesses.append(harness)
            thread = threading.Thread(
                target=lambda current=harness: current.execute_tool(
                    "web_get", {"url": "http://example.com/value"}
                ),
                name=f"bounded-dns-cancel-{index}",
            )
            threads.append(thread)
            thread.start()
            time.sleep(0.02)
            harness.cancel()
            thread.join(timeout=2)
            assert not thread.is_alive()
        resolver_threads = [
            thread
            for thread in threading.enumerate()
            if thread.name.startswith("llm-task-dns-resolver-")
        ]
        assert len(resolver_threads) <= harness_module._DNS_RESOLVER_POOL.workers
    finally:
        release.set()
        for harness in harnesses:
            harness.cancel()
            harness.close()
        for thread in threads:
            thread.join(timeout=3)


@pytest.mark.parametrize(
    "address",
    [
        "100.64.0.1", "::ffff:100.64.0.1", "::ffff:127.0.0.1",
        "224.0.0.1", "239.255.255.250", "ff02::1", "fec0::1",
    ],
)
def test_guarded_http_rejects_every_non_global_resolved_address(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
    address: str,
) -> None:
    family = 10 if ":" in address else 2
    monkeypatch.setattr(
        harness_module.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(family, 1, 6, "", (address, 443, 0, 0))],
    )
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="full-access",
        allow_network=True,
        allowed_hosts=("example.com",),
    ) as harness:
        result = harness.execute_tool("web_get", {"url": "https://example.com/value"})
    assert result["ok"] is False
    assert "non-public network address" in result["error"]["message"]


def test_child_process_environment_excludes_secret_and_bounds_output(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_TASK_SECRET_CANARY", "do-not-leak")
    script = repository / "probe.py"
    script.write_text(
        "import os\nprint(os.environ.get('LLM_TASK_SECRET_CANARY', 'missing'))\nprint('x' * 100)\n",
        encoding="utf-8",
    )
    with LLMTaskHarness(
        scripted(final()),
        repository,
        permission_profile="workspace-write",
        allow_shell=True,
        max_output_bytes=20,
    ) as harness:
        result = harness.execute_tool("shell", {"command": sys.executable, "args": ["probe.py"]})
    assert result["ok"] is True
    assert "do-not-leak" not in result["stdout"]
    assert "missing" in result["stdout"]
    assert len(result["stdout"].encode()) == 20
    assert result["truncated"] is True


def test_state_paths_are_scoped_and_restore_is_validated(repository: Path) -> None:
    state = repository / "runtime" / "state.json"
    with LLMTaskHarness(scripted(final("saved")), repository) as harness:
        harness.run("save")
        harness.save(state)
        with pytest.raises(PermissionError):
            harness.save(repository.parent / "outside.json")
        harness.reset()
        harness.restore(state)
        assert harness.messages


def test_subagents_run_a_real_read_only_tool_loop(repository: Path) -> None:
    def adapter(request: dict[str, object]) -> dict[str, object]:
        messages = request["messages"]
        if messages[-1]["role"] == "tool":
            return final(messages[-1]["content"]["content"].strip())
        return call("read_file", {"path": "README.md"}, call_id=str(len(messages)))

    with LLMTaskHarness(adapter, repository, subagent_limit=2) as harness:
        result = harness.execute_tool("subagents", {"tasks": ["first", "second"]})
    assert result["ok"] is True
    assert [item["content"] for item in result["results"]] == ["hello harness", "hello harness"]


def test_sequential_subagents_share_the_parent_absolute_deadline(repository: Path) -> None:
    def adapter(request: dict[str, object]) -> dict[str, object]:
        messages = request["messages"]
        task = next(
            message["content"]
            for message in reversed(messages)
            if message["role"] == "user"
        )
        if task == "parent" and messages[-1]["role"] != "tool":
            return call("subagents", {"tasks": ["one", "two", "three"]}, "deadline-children")
        if task == "parent":
            return final("parent finished")
        request["cancellation_event"].wait(0.12)
        return final(str(task))

    started = time.monotonic()
    with LLMTaskHarness(
        adapter,
        repository,
        subagent_limit=1,
        timeout=5,
        overall_timeout=0.25,
    ) as harness:
        with pytest.raises(TimeoutError, match="overall timeout"):
            harness.run("parent")
    assert time.monotonic() - started < 0.6


def test_parent_cancellation_reaches_and_quiesces_all_subagents(repository: Path) -> None:
    lock = threading.Lock()
    children_started = threading.Event()
    stopped: set[str] = set()
    active = 0

    def adapter(request: dict[str, object]) -> dict[str, object]:
        nonlocal active
        task = next(
            message["content"]
            for message in reversed(request["messages"])
            if message["role"] == "user"
        )
        if task == "parent":
            return call("subagents", {"tasks": ["child-one", "child-two"]}, "delegate")
        with lock:
            active += 1
            if active == 2:
                children_started.set()
        request["cancellation_event"].wait(5)
        with lock:
            stopped.add(str(task))
        return final()

    harness = LLMTaskHarness(adapter, repository, subagent_limit=2, timeout=30)
    failures: list[BaseException] = []

    def run_parent() -> None:
        try:
            harness.run("parent")
        except BaseException as error:
            failures.append(error)

    thread = threading.Thread(target=run_parent, name="harness-parent-test")
    thread.start()
    try:
        assert children_started.wait(3)
        harness.cancel()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert stopped == {"child-one", "child-two"}
        assert failures and "cancelled" in str(failures[0])
        assert harness._children == set()
    finally:
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


def test_openai_compatible_adapter_normalizes_tools_and_usage() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [{
                    "message": {
                        "content": "",
                        "tool_calls": [{
                            "id": "abc",
                            "type": "function",
                            "function": {"name": "read_file", "arguments": "{\"path\":\"README.md\"}"},
                        }],
                    }
                }],
                "usage": {"total_tokens": 7},
            },
        )

    adapter = OpenAICompatibleAdapter(
        "https://models.example/v1",
        "test-model",
        transport=httpx.MockTransport(handler),
    )
    reply = adapter({
        "instructions": "work carefully",
        "model": "test-model",
        "messages": [{"role": "user", "content": "inspect"}],
        "tools": [{
            "type": "function",
            "name": "read_file",
            "description": "read",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        }],
        "options": {},
    })
    assert captured["tools"][0]["function"]["name"] == "read_file"
    assert captured["messages"][0] == {"role": "system", "content": "work carefully"}
    assert reply["tool_calls"][0]["arguments"] == {"path": "README.md"}
    assert reply["usage"] == {"total_tokens": 7}


def test_openai_adapter_requires_tls_outside_loopback() -> None:
    with pytest.raises(ValueError, match="require HTTPS"):
        OpenAICompatibleAdapter("http://models.example/v1", "test-model")
    local = OpenAICompatibleAdapter("http://127.0.0.1:8801/v1", "test-model")
    assert local.base_url == "http://127.0.0.1:8801/v1"


def test_openai_adapter_cancel_closes_active_provider_client(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    started = threading.Event()
    closed = threading.Event()

    class BlockingClient:
        def __init__(self, *_: object, **__: object) -> None:
            return None

        def post(self, *_: object, **__: object) -> object:
            started.set()
            closed.wait(5)
            raise RuntimeError("provider client closed")

        def close(self) -> None:
            closed.set()

    monkeypatch.setattr(httpx, "Client", BlockingClient)
    adapter = OpenAICompatibleAdapter("http://127.0.0.1:8801/v1", "test-model", timeout=30)
    harness = LLMTaskHarness(adapter, repository, timeout=30)
    failures: list[BaseException] = []

    def run() -> None:
        try:
            harness.run("wait for provider")
        except BaseException as error:
            failures.append(error)

    thread = threading.Thread(target=run, name="openai-adapter-cancel-test")
    thread.start()
    try:
        assert started.wait(3)
        harness.cancel()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert closed.is_set()
        assert failures and "cancelled" in str(failures[0])
    finally:
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


def test_openai_adapter_cancel_during_client_construction_never_dispatches(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    constructing = threading.Event()
    release_constructor = threading.Event()
    post_called = threading.Event()
    closed = threading.Event()

    class ConstructingClient:
        def __init__(self, *_: object, **__: object) -> None:
            constructing.set()
            if not release_constructor.wait(5):
                raise TimeoutError("test did not release provider client construction")

        def post(self, *_: object, **__: object) -> object:
            post_called.set()
            raise AssertionError("cancelled request must not be dispatched")

        def close(self) -> None:
            closed.set()

    monkeypatch.setattr(httpx, "Client", ConstructingClient)
    adapter = OpenAICompatibleAdapter("http://127.0.0.1:8801/v1", "test-model", timeout=30)
    harness = LLMTaskHarness(adapter, repository, timeout=30)
    failures: list[BaseException] = []

    def run() -> None:
        try:
            harness.run("cancel while constructing the provider client")
        except BaseException as error:
            failures.append(error)

    thread = threading.Thread(target=run, name="openai-adapter-construction-cancel-test")
    thread.start()
    try:
        assert constructing.wait(3)
        harness.cancel()
        release_constructor.set()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert not post_called.is_set()
        assert closed.is_set()
        assert failures and "cancelled" in str(failures[0])
    finally:
        release_constructor.set()
        harness.cancel()
        thread.join(timeout=3)
        harness.close()


@pytest.mark.parametrize("cancel_mode", ["timeout", "explicit"])
def test_openai_adapter_cancels_only_its_own_shared_request(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
    cancel_mode: str,
) -> None:
    long_started = threading.Event()
    short_started = threading.Event()

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": "long completed"}}]}

    class RequestClient:
        def __init__(self, *_: object, **__: object) -> None:
            self.closed = threading.Event()

        def post(self, *_: object, **kwargs: object) -> Response:
            payload = kwargs["json"]
            messages = payload["messages"]
            task = next(item["content"] for item in reversed(messages) if item["role"] == "user")
            if task == "short-timeout":
                short_started.set()
                self.closed.wait(5)
                raise RuntimeError("short request closed")
            long_started.set()
            if self.closed.wait(0.4):
                raise RuntimeError("long request was closed by sibling")
            return Response()

        def close(self) -> None:
            self.closed.set()

    monkeypatch.setattr(httpx, "Client", RequestClient)
    adapter = OpenAICompatibleAdapter("http://127.0.0.1:8801/v1", "test-model", timeout=30)
    short_harness = LLMTaskHarness(adapter, repository, timeout=0.15 if cancel_mode == "timeout" else 30)
    long_harness = LLMTaskHarness(adapter, repository, timeout=1)
    short_failures: list[BaseException] = []
    long_results: list[str] = []
    long_failures: list[BaseException] = []

    def run_short() -> None:
        try:
            short_harness.run("short-timeout")
        except BaseException as error:
            short_failures.append(error)

    def run_long() -> None:
        try:
            long_results.append(long_harness.run("long-request"))
        except BaseException as error:
            long_failures.append(error)

    long_thread = threading.Thread(target=run_long, name="shared-adapter-long-test")
    short_thread = threading.Thread(target=run_short, name="shared-adapter-short-test")
    long_thread.start()
    try:
        assert long_started.wait(3)
        short_thread.start()
        assert short_started.wait(3)
        if cancel_mode == "explicit":
            short_harness.cancel()
        short_thread.join(timeout=3)
        long_thread.join(timeout=3)
        assert not short_thread.is_alive()
        assert not long_thread.is_alive()
        assert short_failures
        if cancel_mode == "timeout":
            assert isinstance(short_failures[0], TimeoutError)
        else:
            assert "cancelled" in str(short_failures[0])
        assert long_failures == []
        assert long_results == ["long completed"]
    finally:
        short_harness.cancel()
        long_harness.cancel()
        short_thread.join(timeout=3)
        long_thread.join(timeout=3)
        short_harness.close()
        long_harness.close()


def test_manager_pauses_for_approval_then_completes(repository: Path) -> None:
    adapter = scripted(call("write_file", {"path": "answer.txt", "content": "approved\n"}, "write-1"), final("done"))
    settings = {
        "executionEnabled": True,
        "defaultPermissionProfile": "workspace-write",
        "defaultApprovalMode": "on-request",
        "maxWorkers": 1,
        "maxSteps": 5,
        "modelTimeoutSeconds": 5,
        "taskTimeoutSeconds": 30,
    }
    manager = HarnessTaskManager(repository, settings, adapter_factory=lambda _: adapter)
    try:
        task = manager.submit({"task": "write the answer"})
        waiting = wait_for(manager, task["id"], {"waiting_approval"})
        assert waiting["approvals"]["write-1"]["tool"] == "write_file"
        manager.decide_approval(task["id"], "write-1", "allow")
        completed = wait_for(manager, task["id"], {"completed", "failed"})
        assert completed["status"] == "completed", completed
        assert (repository / "answer.txt").read_text(encoding="utf-8") == "approved\n"
        events = manager.events(task["id"])
        assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
        assert {event["event"] for event in events} >= {
            "task.queued", "task.started", "approval.requested", "approval.resolved", "task.completed"
        }
    finally:
        manager.close()


def test_manager_pauses_for_human_input(repository: Path) -> None:
    adapter = scripted(call("request_user_input", {"prompt": "Which target?"}, "input-1"), final("received"))
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
            "maxSteps": 5,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "ask"})
        waiting = wait_for(manager, task["id"], {"waiting_input"})
        assert waiting["pendingInput"]["prompt"] == "Which target?"
        manager.provide_input(task["id"], "alpha")
        completed = wait_for(manager, task["id"], {"completed", "failed"})
        assert completed["status"] == "completed", completed
        tool_message = adapter.requests[1]["messages"][-1]
        assert tool_message["content"]["response"] == "alpha"
    finally:
        manager.close()


def test_manager_does_not_report_terminal_until_noncooperative_adapter_exits(repository: Path) -> None:
    release = threading.Event()
    started = threading.Event()

    def blocked(_: dict[str, object]) -> dict[str, object]:
        started.set()
        release.wait(10)
        return final()

    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "defaultApprovalMode": "never",
            "allowApprovalNever": True,
            "maxWorkers": 1,
            "maxSteps": 5,
            "modelTimeoutSeconds": 30,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: blocked,
    )
    try:
        task = manager.submit({"task": "wait"})
        wait_for(manager, task["id"], {"running"})
        assert started.wait(2)
        requested = manager.cancel(task["id"])
        time.sleep(0.15)
        pending = manager.get(task["id"])
        assert requested["cancelRequested"] is True
        assert pending["status"] not in manager.TERMINAL
        release.set()
        cancelled = wait_for(manager, task["id"], {"cancelled", "failed"})
        assert cancelled["status"] == "cancelled"
    finally:
        release.set()
        manager.close()


def test_manager_cooperative_adapter_quiesces_before_terminal_cancellation(repository: Path) -> None:
    started = threading.Event()
    stopped = threading.Event()

    def cooperative(request: dict[str, object]) -> dict[str, object]:
        cancellation = request["cancellation_event"]
        started.set()
        cancellation.wait(5)
        stopped.set()
        return final()

    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
            "maxSteps": 5,
            "modelTimeoutSeconds": 30,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: cooperative,
    )
    try:
        task = manager.submit({"task": "wait cooperatively"})
        assert started.wait(2)
        manager.cancel(task["id"])
        cancelled = wait_for(manager, task["id"], {"cancelled", "failed"})
        assert cancelled["status"] == "cancelled"
        assert stopped.is_set()
        assert not any(
            thread.name == "llm-task-model-call" and thread.is_alive()
            for thread in threading.enumerate()
        )
    finally:
        manager.close()


def test_restart_marks_nonterminal_record_interrupted(repository: Path) -> None:
    task_id = "00000000-0000-0000-0000-000000000001"
    directory = repository / "runtime" / "pycoplex" / "tasks"
    directory.mkdir(parents=True)
    (directory / f"{task_id}.json").write_text(
        json.dumps({
            "id": task_id,
            "task": "unfinished",
            "root": ".",
            "model": "test",
            "permissionProfile": "read-only",
            "approvalMode": "never",
            "status": "running",
            "createdAt": 1,
            "updatedAt": 1,
            "startedAt": 1,
            "finishedAt": None,
            "answer": "",
            "error": "",
            "cancelRequested": False,
            "approvals": {},
            "pendingInput": None,
            "inputResponse": None,
            "options": {},
        }),
        encoding="utf-8",
    )
    manager = HarnessTaskManager(repository, {"executionEnabled": False})
    try:
        recovered = manager.get(task_id)
        assert recovered["status"] == "interrupted"
        assert "stopped" in recovered["error"]
    finally:
        manager.close()


def test_manager_rejects_execution_until_explicitly_enabled(repository: Path) -> None:
    manager = HarnessTaskManager(repository, {"executionEnabled": False})
    try:
        with pytest.raises(PermissionError, match="disabled"):
            manager.submit({"task": "do not run"})
    finally:
        manager.close()


def test_closed_manager_rejects_submit_without_persisting_a_queued_record(repository: Path) -> None:
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "maximumPermissionProfile": "read-only",
            "defaultApprovalMode": "on-request",
        },
        adapter_factory=lambda _: scripted(final()),
    )
    manager.close()
    with pytest.raises(RuntimeError, match="closed"):
        manager.submit({"task": "must not be queued"})
    assert manager.list() == []
    assert list((repository / "runtime" / "pycoplex" / "tasks").iterdir()) == []


def test_manager_enforces_permission_and_approval_ceiling(repository: Path) -> None:
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "workspace-write",
            "maximumPermissionProfile": "workspace-write",
            "defaultApprovalMode": "on-request",
            "allowApprovalNever": False,
        },
        adapter_factory=lambda _: scripted(final()),
    )
    try:
        with pytest.raises(PermissionError, match="exceeds configured maximum"):
            manager.submit({"task": "too much authority", "permissionProfile": "full-access"})
        with pytest.raises(PermissionError, match="never is disabled"):
            manager.submit({"task": "skip approvals", "approvalMode": "never"})
        with pytest.raises(PermissionError, match="control-plane"):
            manager.submit({"task": "inspect task state", "root": "runtime/pycoplex"})
    finally:
        manager.close()


def test_manager_persists_transcript_for_nested_task_root(repository: Path) -> None:
    nested = repository / "project"
    nested.mkdir()
    adapter = scripted(final("nested complete"))
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "defaultApprovalMode": "never",
            "allowApprovalNever": True,
            "maxWorkers": 1,
            "maxSteps": 2,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "inspect nested", "root": "project"})
        completed = wait_for(manager, task["id"], {"completed", "failed"})
        assert completed["status"] == "completed", completed
        transcript = (
            repository
            / "runtime"
            / "pycoplex"
            / "tasks"
            / f"{task['id']}.transcript.jsonl"
        )
        messages = [json.loads(line) for line in transcript.read_text(encoding="utf-8").splitlines()]
        assert [message["role"] for message in messages] == ["system", "user", "assistant"]
        assert messages[-1]["content"] == "nested complete"
    finally:
        manager.close()


def test_manager_rejects_denied_directories_as_task_roots(repository: Path) -> None:
    (repository / ".credentials").mkdir()
    (repository / "nested" / ".git").mkdir(parents=True)
    (repository / "vault.key").mkdir()
    manager = HarnessTaskManager(repository, {"executionEnabled": False})
    try:
        for value in (".git", ".credentials", "nested/.git", "vault.key"):
            with pytest.raises(PermissionError, match="denied by harness policy"):
                manager._task_root(value)
    finally:
        manager.close()


@pytest.mark.parametrize("target_kind", ["outside", "denied"])
def test_manager_rejects_symlinked_ancestor_instruction_targets(
    repository: Path,
    target_kind: str,
) -> None:
    nested = repository / "nested"
    nested.mkdir()
    target = (
        repository.parent / "outside-agents.txt"
        if target_kind == "outside"
        else repository / ".env"
    )
    target.write_text(f"{target_kind}-instruction-canary\n", encoding="utf-8")
    try:
        (repository / "AGENTS.md").symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlinks unavailable: {error}")
    manager = HarnessTaskManager(repository, {"executionEnabled": False})
    try:
        assert manager._ancestor_instruction_context(nested) is None
    finally:
        manager.close()


def test_manager_bounds_ancestor_instruction_reads(repository: Path) -> None:
    nested = repository / "nested"
    nested.mkdir()
    (repository / "AGENTS.md").write_text("x" * 5000, encoding="utf-8")
    manager = HarnessTaskManager(
        repository,
        {"executionEnabled": False, "maxContextBytes": 1024},
    )
    try:
        with pytest.raises(ValueError, match="instructions exceed"):
            manager._ancestor_instruction_context(nested)
    finally:
        manager.close()


def test_manager_control_plane_files_are_denied_to_tasks(repository: Path) -> None:
    adapter = scripted(
        call("read_file", {"path": "runtime/pycoplex/tasks/hidden.json"}),
        final("control plane protected"),
    )
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "defaultApprovalMode": "never",
            "allowApprovalNever": True,
            "maxWorkers": 1,
            "maxSteps": 3,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "try the control plane"})
        completed = wait_for(manager, task["id"], {"completed", "failed"})
        assert completed["status"] == "completed", completed
        result = adapter.requests[1]["messages"][-1]["content"]
        assert result["ok"] is False
        assert "denied by policy" in result["error"]["message"]
    finally:
        manager.close()


def test_manager_ignores_forged_record_ids(repository: Path) -> None:
    directory = repository / "runtime" / "pycoplex" / "tasks"
    directory.mkdir(parents=True)
    forged = directory / "forged.json"
    forged.write_text(
        json.dumps({
            "id": "../../outside",
            "task": "malicious recovery record",
            "status": "running",
        }),
        encoding="utf-8",
    )
    manager = HarnessTaskManager(repository, {"executionEnabled": False})
    try:
        assert manager.list() == []
        assert forged.is_file()
        assert not (repository / "outside.json").exists()
    finally:
        manager.close()


def test_manager_task_timeout_applies_while_waiting_for_approval(repository: Path) -> None:
    adapter = scripted(
        call("write_file", {"path": "late.txt", "content": "too late"}, "late-write"),
        final("should not finish"),
    )
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "workspace-write",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
            "maxSteps": 3,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 1,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "wait for an approval that never comes"})
        wait_for(manager, task["id"], {"waiting_approval"})
        failed = wait_for(manager, task["id"], {"failed"}, timeout=3)
        assert "timed out while waiting for approval" in failed["error"]
        assert failed["approvals"]["late-write"]["status"] == "expired"
        assert not (repository / "late.txt").exists()
    finally:
        manager.close()


def test_manager_initialization_failure_becomes_terminal(repository: Path) -> None:
    def broken_factory(_: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("adapter construction failed")

    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "maximumPermissionProfile": "read-only",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
        },
        adapter_factory=broken_factory,
    )
    try:
        task = manager.submit({"task": "fail during setup"})
        failed = wait_for(manager, task["id"], {"failed"})
        assert "adapter construction failed" in failed["error"]
    finally:
        manager.close()


def test_cancelled_task_rejects_late_approval(repository: Path) -> None:
    adapter = scripted(
        call("write_file", {"path": "cancelled.txt", "content": "no"}, "cancel-write"),
        final("should not complete"),
    )
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "workspace-write",
            "maximumPermissionProfile": "workspace-write",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
            "maxSteps": 3,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "cancel at approval"})
        wait_for(manager, task["id"], {"waiting_approval"})
        manager.cancel(task["id"])
        cancelled = wait_for(manager, task["id"], {"cancelled"})
        assert cancelled["approvals"]["cancel-write"]["status"] == "cancelled"
        with pytest.raises(ValueError, match="no longer accepting"):
            manager.decide_approval(task["id"], "cancel-write", "allow")
        assert not (repository / "cancelled.txt").exists()
    finally:
        manager.close()


def test_nested_task_receives_ancestor_agents_instructions(repository: Path) -> None:
    (repository / "AGENTS.md").write_text("root-instruction-canary\n", encoding="utf-8")
    nested = repository / "nested"
    nested.mkdir()
    adapter = scripted(final("context received"))
    manager = HarnessTaskManager(
        repository,
        {
            "executionEnabled": True,
            "defaultPermissionProfile": "read-only",
            "maximumPermissionProfile": "read-only",
            "defaultApprovalMode": "on-request",
            "maxWorkers": 1,
            "maxSteps": 2,
            "modelTimeoutSeconds": 5,
            "taskTimeoutSeconds": 30,
        },
        adapter_factory=lambda _: adapter,
    )
    try:
        task = manager.submit({"task": "inspect nested", "root": "nested"})
        completed = wait_for(manager, task["id"], {"completed", "failed"})
        assert completed["status"] == "completed", completed
        context = adapter.requests[0]["messages"][0]["content"]
        assert "root-instruction-canary" in context
    finally:
        manager.close()


def test_overall_timeout_terminates_running_process(repository: Path) -> None:
    script = repository / "slow_writer.py"
    script.write_text(
        "import pathlib, time\n"
        "pathlib.Path('process_started.txt').write_text('started')\n"
        "time.sleep(2)\n"
        "pathlib.Path('orphan.txt').write_text('orphan')\n",
        encoding="utf-8",
    )
    adapter = scripted(call("shell", {"command": sys.executable, "args": ["slow_writer.py"]}))
    with LLMTaskHarness(
        adapter,
        repository,
        permission_profile="workspace-write",
        allow_shell=True,
        timeout=5,
        overall_timeout=1,
    ) as harness:
        with pytest.raises(TimeoutError, match="overall timeout"):
            harness.run("start the slow process")
    assert (repository / "process_started.txt").read_text(encoding="utf-8") == "started"
    time.sleep(2.1)
    assert not (repository / "orphan.txt").exists()
