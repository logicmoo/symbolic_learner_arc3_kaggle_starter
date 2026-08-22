"""Lightweight smoke tests for every emulated /v1 surface in llm_emul_api.

These deliberately stay small: for endpoints that don't need a connected
worker (models listing, embeddings, moderations, images, audio stubs, and
the files/assistants/threads/fine_tuning CRUD stubs) we just check a 200
and the expected shape. For the worker-relayed endpoints (chat
completions, completions, responses), no worker is connected in this test
process; the relay is designed to wait (not fail fast) for one, so these
tests monkeypatch a short timeout and just assert the eventual 504 --
the actual relay round-trip (including the /llm_emul/{worker_id}/ws
handshake) is exercised manually via scripts/llm_emul_worker.py against a
live server.

Multi-worker routing, capability-gated "pretend" modes, and rate
limiting are exercised directly against the module's internal state
(registering a FakeWorker under _connected_workers), since driving a real
websocket handshake end-to-end isn't worth the weight for a smoke suite.
"""
from __future__ import annotations

import asyncio
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from llm_emul import api as llm_emul_api


class FakeWorker:
    """A worker double: records every payload sent to it and can be told
    to answer with a canned reply."""

    def __init__(self, reply: str | None = None) -> None:
        self.sent: list[dict] = []
        self.reply = reply

    async def send_json(self, payload: dict) -> None:
        self.sent.append(payload)
        future = llm_emul_api._pending.get(payload["id"])  # noqa: SLF001
        if future and not future.done() and self.reply is not None:
            future.set_result(self.reply)


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_emul_api.router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_llm_emul_state(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The files/assistants/threads/fine_tuning-job stubs (and the tokens
    # store) persist to disk (see _JsonRecordStore) so they survive a
    # real server restart; for tests, redirect each store to a throwaway
    # tmp_path dir instead of touching the real
    # workbench/server/runtime/llm_emul/ directory.
    for store in (
        llm_emul_api._files_store,
        llm_emul_api._assistants_store,
        llm_emul_api._threads_store,
        llm_emul_api._fine_tuning_jobs_store,
        llm_emul_api._tokens_store,
    ):
        monkeypatch.setattr(store, "_dir", tmp_path / store._dir.name)

    # Reset all module-level relay/routing/usage state so tests don't leak
    # into each other (e.g. rate-limit counters accumulating across tests,
    # or a FakeWorker registered by one test still being "connected" for
    # the next one).
    monkeypatch.setattr(llm_emul_api, "_connected_workers", {})
    monkeypatch.setattr(llm_emul_api, "_worker_models", {})
    monkeypatch.setattr(llm_emul_api, "_worker_capabilities", {})
    monkeypatch.setattr(llm_emul_api, "_worker_usage", {})
    monkeypatch.setattr(llm_emul_api, "_pending", {})
    # /llm_emul/storage/* derives its root from _RUNTIME_DIR directly, so
    # isolate that too instead of touching the real runtime/llm_emul/ dir.
    monkeypatch.setattr(llm_emul_api, "_RUNTIME_DIR", tmp_path / "runtime")


def test_list_models_includes_personas(client: TestClient) -> None:
    data = client.get("/v1/models").json()["data"]
    ids = {entry["id"] for entry in data}
    assert ids == {
        "yourself/same",
        "yourself/percent125",
        "yourself/percent100",
        "yourself/percent75",
        "yourself/percent25",
        "yourself/percent10",
    }


def test_get_single_model(client: TestClient) -> None:
    response = client.get("/v1/models/yourself/percent25")
    assert response.status_code == 200
    assert response.json()["id"] == "yourself/percent25"
    # A bare/unknown worker_id still resolves (falls back to the default
    # persona menu -- see _models_for), but an unknown SUFFIX never does.
    assert client.get("/v1/models/yourself/no-such-suffix").status_code == 404


@pytest.fixture()
def short_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    # Without this, "no worker connected" would wait the full (900s)
    # production timeout before giving up -- these tests want that to
    # happen almost instantly instead.
    monkeypatch.setattr(llm_emul_api, "_REQUEST_TIMEOUT_SECONDS", 0.3)


def test_chat_completions_without_worker_waits_then_504(client: TestClient, short_timeout: None) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={"model": "yourself/same", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 504


def test_completions_without_worker_waits_then_504(client: TestClient, short_timeout: None) -> None:
    response = client.post("/v1/completions", json={"model": "yourself/same", "prompt": "hi"})
    assert response.status_code == 504


def test_responses_without_worker_waits_then_504(client: TestClient, short_timeout: None) -> None:
    response = client.post("/v1/responses", json={"model": "yourself/same", "input": "hi"})
    assert response.status_code == 504


def test_relay_waits_for_late_worker_instead_of_failing_fast() -> None:
    """Simulates a request landing while no worker is connected: _relay
    must NOT fail fast -- it should wait (like a slow API server) and
    succeed once a worker connects and replies."""

    async def scenario() -> str:
        async def connect_worker_after_delay() -> None:
            await asyncio.sleep(0.2)
            worker = FakeWorker(reply="answered late")
            llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001

        relay_task = asyncio.create_task(llm_emul_api._relay("yourself/same", "hello"))
        connector_task = asyncio.create_task(connect_worker_after_delay())
        result = await relay_task
        await connector_task
        return result

    original_timeout = llm_emul_api._REQUEST_TIMEOUT_SECONDS
    llm_emul_api._REQUEST_TIMEOUT_SECONDS = 5
    try:
        result = asyncio.run(scenario())
    finally:
        llm_emul_api._REQUEST_TIMEOUT_SECONDS = original_timeout

    assert result == "answered late"


def test_relay_routes_to_the_worker_matching_the_model_prefix() -> None:
    """Two different worker_ids can be "logged in" at once; a request for
    "alice/same" must go to alice's connection, not bob's (or "yourself")."""
    alice = FakeWorker(reply="alice answered")
    bob = FakeWorker(reply="bob answered")
    llm_emul_api._connected_workers["alice"] = alice  # noqa: SLF001
    llm_emul_api._connected_workers["bob"] = bob  # noqa: SLF001

    result = asyncio.run(llm_emul_api._relay("alice/same", "hi"))

    assert result == "alice answered"
    assert len(alice.sent) == 1
    assert not bob.sent


def test_list_models_aggregates_every_connected_worker(client: TestClient) -> None:
    llm_emul_api._connected_workers["alice"] = FakeWorker()  # noqa: SLF001
    llm_emul_api._worker_models["alice"] = {"same": {"display_name": "(alice)", "instruction": "Be alice."}}

    ids = {entry["id"] for entry in client.get("/v1/models").json()["data"]}
    assert "alice/same" in ids
    assert "yourself/same" in ids  # the default identity is always advertised


def test_worker_caps_lookup(client: TestClient) -> None:
    assert client.get("/llm_emul/caps/yourself").json() == {
        "worker_id": "yourself",
        "connected": False,
        "models": sorted(llm_emul_api._PERSONA_SUFFIXES.keys()),
        "capabilities": {},
    }

    llm_emul_api._connected_workers["alice"] = FakeWorker()  # noqa: SLF001
    llm_emul_api._worker_capabilities["alice"] = {"images": True}

    result = client.get("/llm_emul/caps/alice").json()
    assert result["connected"] is True
    assert result["capabilities"] == {"images": True}


def test_serve_doc_returns_a_real_markdown_file(client: TestClient) -> None:
    response = client.get("/llm_emul/docs/design/LLM_EMUL_RELAY.md")
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "llm_emul" in response.text.lower()


def test_serve_join_as_worker_doc(client: TestClient) -> None:
    response = client.get("/llm_emul/docs/LLM_EMUL_ONBOARDING.md")
    assert response.status_code == 200
    assert "text/markdown" in response.headers["content-type"]
    assert "worker" in response.text.lower()


def test_serve_doc_404s_for_missing_file(client: TestClient) -> None:
    assert client.get("/llm_emul/docs/no-such-file.md").status_code == 404


def test_serve_doc_rejects_path_traversal(client: TestClient) -> None:
    assert client.get("/llm_emul/docs/../server/llm_emul_api.py").status_code in (400, 404)


def test_specific_worker_prefix_pins_worker_regardless_of_model_field(client: TestClient, short_timeout: None) -> None:
    """A client hitting /llm_emul/specific_worker/alice/v1/chat/completions
    must be routed to alice even if it sends a "model" naming someone
    else (or the default) -- only the persona suffix is kept."""
    alice = FakeWorker(reply="alice's real answer")
    llm_emul_api._connected_workers["alice"] = alice  # noqa: SLF001
    bob = FakeWorker(reply="bob would never see this")
    llm_emul_api._connected_workers["bob"] = bob  # noqa: SLF001

    response = client.post(
        "/llm_emul/specific_worker/alice/v1/chat/completions",
        json={"model": "bob/percent25", "messages": [{"role": "user", "content": "hi"}]},
    )

    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "alice's real answer"
    assert not bob.sent
    assert alice.sent[0]["model"] == "alice/percent25"  # worker_id forced, suffix kept


def test_specific_worker_models_listing_is_scoped_to_that_worker(client: TestClient) -> None:
    llm_emul_api._worker_models["alice"] = {"same": {"display_name": "(alice)", "instruction": "Be alice."}}

    data = client.get("/llm_emul/specific_worker/alice/v1/models").json()["data"]

    assert {entry["id"] for entry in data} == {"alice/same"}


def test_specific_worker_get_model_and_404(client: TestClient) -> None:
    assert client.get("/llm_emul/specific_worker/alice/v1/models/anything/same").status_code == 200
    assert client.get("/llm_emul/specific_worker/alice/v1/models/anything/no-such-suffix").status_code == 404


def test_rate_limit_returns_429_with_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    """Once a worker_id has been used up to the configured limit within
    the window, further requests for it fail fast with 429 and a
    Retry-After, instead of queuing more work onto a busy worker."""
    monkeypatch.setattr(llm_emul_api, "_USAGE_MAX_PER_WINDOW", 2)
    monkeypatch.setattr(llm_emul_api, "_USAGE_WINDOW_SECONDS", 60.0)
    worker = FakeWorker(reply="ok")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001

    asyncio.run(llm_emul_api._relay("yourself/same", "one"))
    asyncio.run(llm_emul_api._relay("yourself/same", "two"))

    with pytest.raises(llm_emul_api.HTTPException) as excinfo:
        asyncio.run(llm_emul_api._relay("yourself/same", "three"))
    assert excinfo.value.status_code == 429
    assert "Retry-After" in excinfo.value.headers


def test_rate_limit_is_independent_per_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    """A different worker_id isn't affected by another one being maxed
    out -- so an idle worker can pick up slack for a busy one."""
    monkeypatch.setattr(llm_emul_api, "_USAGE_MAX_PER_WINDOW", 1)
    monkeypatch.setattr(llm_emul_api, "_USAGE_WINDOW_SECONDS", 60.0)
    llm_emul_api._connected_workers["alice"] = FakeWorker(reply="a")  # noqa: SLF001
    llm_emul_api._connected_workers["bob"] = FakeWorker(reply="b")  # noqa: SLF001

    asyncio.run(llm_emul_api._relay("alice/same", "hi"))
    with pytest.raises(llm_emul_api.HTTPException):
        asyncio.run(llm_emul_api._relay("alice/same", "hi again"))

    # bob is untouched by alice's limit
    assert asyncio.run(llm_emul_api._relay("bob/same", "hi")) == "b"


def test_embeddings_is_deterministic_without_pretend_capability(client: TestClient) -> None:
    first = client.post("/v1/embeddings", json={"input": "hello"}).json()
    second = client.post("/v1/embeddings", json={"input": "hello"}).json()
    assert first["data"][0]["embedding"] == second["data"][0]["embedding"]
    assert len(first["data"][0]["embedding"]) == 8


def test_embeddings_pretend_mode_routes_to_the_capable_worker(client: TestClient) -> None:
    worker = FakeWorker(reply="a vector about greetings")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"embeddings": True}

    client.post("/v1/embeddings", json={"input": "hello"})

    assert len(worker.sent) == 1
    assert "pretend-embeddings" in worker.sent[0]["prompt"]


def test_embeddings_declined_capability_stops_before_asking_worker(client: TestClient) -> None:
    worker = FakeWorker(reply="should never be used")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"embeddings": False}  # explicit decline

    response = client.post("/v1/embeddings", json={"input": "hello"})

    assert response.status_code == 501
    assert not worker.sent  # never even asked


def test_moderations_never_flags_without_pretend_capability(client: TestClient) -> None:
    result = client.post("/v1/moderations", json={"input": "anything"}).json()
    assert result["results"][0]["flagged"] is False


def test_moderations_pretend_mode_uses_worker_verdict(client: TestClient) -> None:
    llm_emul_api._connected_workers["yourself"] = FakeWorker(reply="FLAG")  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"moderations": True}

    result = client.post("/v1/moderations", json={"input": "anything"}).json()

    assert result["results"][0]["flagged"] is True


def test_moderations_declined_capability_stops_before_asking_worker(client: TestClient) -> None:
    worker = FakeWorker(reply="should never be used")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"moderations": False}

    response = client.post("/v1/moderations", json={"input": "anything"})

    assert response.status_code == 501
    assert not worker.sent


def test_images_generations_returns_stub_url(client: TestClient) -> None:
    result = client.post("/v1/images/generations", json={"prompt": "a cat"}).json()
    assert result["data"][0]["url"].startswith("data:image/png;base64,")
    assert "pretend_description" not in result["data"][0]


def test_images_generations_pretend_mode_adds_description(client: TestClient) -> None:
    llm_emul_api._connected_workers["yourself"] = FakeWorker(reply="a fluffy orange cat")  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"images": True}

    result = client.post("/v1/images/generations", json={"prompt": "a cat"}).json()

    assert result["data"][0]["pretend_description"] == "a fluffy orange cat"


def test_images_declined_capability_stops_before_asking_worker(client: TestClient) -> None:
    worker = FakeWorker(reply="should never be used")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"images": False}

    response = client.post("/v1/images/generations", json={"prompt": "a cat"})

    assert response.status_code == 501
    assert not worker.sent


def test_audio_transcriptions_is_stub(client: TestClient) -> None:
    result = client.post("/v1/audio/transcriptions").json()
    assert "not implemented" in result["text"]


def test_audio_transcriptions_pretend_mode_uses_worker_text(client: TestClient) -> None:
    llm_emul_api._connected_workers["yourself"] = FakeWorker(reply="hello there")  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"audio_transcription": True}

    result = client.post("/v1/audio/transcriptions").json()

    assert result["text"] == "hello there"


def test_audio_transcriptions_declined_capability_stops_before_asking_worker(client: TestClient) -> None:
    worker = FakeWorker(reply="should never be used")
    llm_emul_api._connected_workers["yourself"] = worker  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"audio_transcription": False}

    response = client.post("/v1/audio/transcriptions")

    assert response.status_code == 501
    assert not worker.sent


def test_audio_speech_is_stub(client: TestClient) -> None:
    result = client.post("/v1/audio/speech", json={"input": "hi"}).json()
    assert "not implemented" in result["note"]


def test_audio_speech_pretend_mode_adds_description(client: TestClient) -> None:
    llm_emul_api._connected_workers["yourself"] = FakeWorker(reply="said cheerfully")  # noqa: SLF001
    llm_emul_api._worker_capabilities["yourself"] = {"audio_speech": True}

    result = client.post("/v1/audio/speech", json={"input": "hi"}).json()

    assert result["pretend_description"] == "said cheerfully"


@pytest.mark.parametrize(
    "path",
    ["/v1/files", "/v1/assistants", "/v1/threads", "/v1/fine_tuning/jobs"],
)
def test_crud_stub_list_then_create(client: TestClient, path: str) -> None:
    assert client.get(path).json() == {"object": "list", "data": []}
    created = client.post(path, json={"note": "test"}).json()
    assert created["id"]
    listed = client.get(path).json()["data"]
    assert any(item["id"] == created["id"] for item in listed)


def test_crud_stub_persists_to_a_json_file_per_record(client: TestClient) -> None:
    created = client.post("/v1/files", json={"note": "durable"}).json()
    record_path = llm_emul_api._files_store._dir / f"{created['id']}.json"
    assert record_path.exists()
    on_disk = json.loads(record_path.read_text(encoding="utf-8"))
    assert on_disk["note"] == "durable"


def test_storage_round_trip_put_get_delete(client: TestClient) -> None:
    assert client.get("/llm_emul/storage").json() == {"files": []}
    assert client.get("/llm_emul/storage/notes/todo.txt").status_code == 404

    put_response = client.put("/llm_emul/storage/notes/todo.txt", content=b"remember this")
    assert put_response.status_code == 200
    assert put_response.json() == {"path": "notes/todo.txt", "bytes": len(b"remember this")}

    assert client.get("/llm_emul/storage").json() == {"files": ["notes/todo.txt"]}
    get_response = client.get("/llm_emul/storage/notes/todo.txt")
    assert get_response.status_code == 200
    assert get_response.content == b"remember this"

    delete_response = client.delete("/llm_emul/storage/notes/todo.txt")
    assert delete_response.status_code == 200
    assert client.get("/llm_emul/storage/notes/todo.txt").status_code == 404


def test_storage_rejects_path_traversal(client: TestClient) -> None:
    # The HTTP client normalizes ".." before it's even sent in some cases,
    # so either FastAPI's routing 404s on the resulting path, or our own
    # _safe_storage_path guard rejects it with 400 -- both are acceptable,
    # the important thing is neither one ever escapes the storage root.
    assert client.get("/llm_emul/storage/../../etc/passwd").status_code in (400, 404)
    assert client.put("/llm_emul/storage/../escape.txt", content=b"x").status_code in (400, 404)


def test_admin_state_reports_connected_workers_and_usage(client: TestClient) -> None:
    llm_emul_api._connected_workers["alice"] = FakeWorker(reply="ok")  # noqa: SLF001
    asyncio.run(llm_emul_api._relay("alice/same", "hi"))

    state = client.get("/admin/llm_emul/state").json()

    assert "alice" in state["connected_worker_ids"]
    assert state["worker_usage"]["alice"]["total_requests"] == 1


def test_admin_runtime_dir_and_reset(client: TestClient, tmp_path) -> None:
    new_dir = tmp_path / "moved"
    client.post("/admin/llm_emul/runtime_dir", json={"path": str(new_dir)})
    client.post("/v1/files", json={"note": "x"})
    assert client.get("/v1/files").json()["data"]

    client.post("/admin/llm_emul/reset")

    assert client.get("/v1/files").json()["data"] == []


def test_admin_delete_record(client: TestClient) -> None:
    created = client.post("/v1/files", json={"note": "x"}).json()
    assert client.delete(f"/admin/llm_emul/records/files/{created['id']}").status_code == 200
    assert client.get("/v1/files").json()["data"] == []
    assert client.delete(f"/admin/llm_emul/records/files/{created['id']}").status_code == 404
    assert client.delete("/admin/llm_emul/records/no-such-kind/x").status_code == 404


def test_admin_routes_have_an_llm_emul_admin_alias(client: TestClient) -> None:
    """/llm_emul/admin/* must behave identically to /admin/llm_emul/*."""
    assert client.get("/llm_emul/admin/state").json() == client.get("/admin/llm_emul/state").json()

    created = client.post("/v1/files", json={"note": "via alias"}).json()
    reset_via_alias = client.post("/llm_emul/admin/reset").json()
    assert reset_via_alias["removed"]["files"] == 1
    assert client.get("/v1/files").json()["data"] == []

    created = client.post("/v1/files", json={"note": "delete via alias"}).json()
    assert client.delete(f"/llm_emul/admin/records/files/{created['id']}").status_code == 200
    assert client.get("/v1/files").json()["data"] == []

    llm_emul_api._connected_workers["yourself"] = FakeWorker(reply="ok")  # noqa: SLF001
    asyncio.run(llm_emul_api._relay("yourself/same", "hi"))
    client.post("/llm_emul/admin/usage/reset")
    assert client.get("/admin/llm_emul/state").json()["worker_usage"] == {}


def test_tokens_new_page_is_html(client: TestClient) -> None:
    response = client.get("/llm_emul/tokens/new")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Get a token" in response.text


def test_create_token_requires_email(client: TestClient) -> None:
    assert client.post("/llm_emul/tokens", json={}).status_code == 422  # missing required field
    assert client.post("/llm_emul/tokens", json={"email": "  "}).status_code == 400


def test_create_token_generates_one_by_default(client: TestClient) -> None:
    result = client.post("/llm_emul/tokens", json={"email": "a@example.com"}).json()
    assert result["id"]
    assert result["email"] == "a@example.com"
    assert llm_emul_api.is_valid_token(result["id"]) is True
    assert llm_emul_api.is_valid_token("not-a-real-token") is False


def test_create_token_accepts_a_bring_your_own_token(client: TestClient) -> None:
    result = client.post("/llm_emul/tokens", json={"email": "a@example.com", "token": "my-own-token"}).json()
    assert result["id"] == "my-own-token"
    assert llm_emul_api.is_valid_token("my-own-token") is True


def test_create_token_can_register_a_public_key(client: TestClient) -> None:
    pubkey = "ssh-ed25519 AAAAtest a@example.com"
    client.post("/llm_emul/tokens", json={"email": "a@example.com", "public_key": pubkey})
    assert llm_emul_api.is_registered_public_key(pubkey) is True
    assert llm_emul_api.is_registered_public_key("ssh-ed25519 AAAAnope") is False
