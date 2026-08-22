"""Simulated LLM backend: relay chat-completion requests to a human or
agent connected over a WebSocket, instead of a real model API.

Exposes an OpenAI-compatible surface so it can be registered as an
ordinary local, keyless backend in the workbench's Models page (baseUrl
"http://127.0.0.1:8000/v1", adapter "openai_chat_completions" -- see
workbench/workspaces/shared_library_system/design/backends/llm_emul.backend.metta).

Implemented routes, and how each is emulated:
  - GET  /v1/models                 -- list personas (see list_models())
  - GET  /v1/models/{model_id}       -- fetch one persona's metadata
  - GET  /llm_emul/caps/{worker_id}  -- lightweight per-worker lookup:
                                         connected?, its models, and its
                                         declared "pretend" capabilities
  - GET  /llm_emul/docs/{rel_path}   -- serves this feature's own design
                                         docs (workbench/docs/**) straight
                                         off disk, e.g.
                                         /llm_emul/docs/design/LLM_EMUL_RELAY.md
  - GET  /llm_emul/tokens/new        -- tiny HTML page: give an email,
                                         get a generated token (or bring
                                         your own token/SSH public key to
                                         register instead)
  - POST /llm_emul/tokens            -- the JSON API behind that page
  - /llm_emul/storage/{path}         -- GET/PUT/DELETE generic durable
                                         blobs (a worker "borrowing" this
                                         server's disk for its own scratch
                                         space), plus GET /llm_emul/storage
                                         to list everything stored
  - /llm_emul/specific_worker/{worker_id}/v1/*
                                     -- the SAME /v1/* surface (models,
                                         chat/completions, completions,
                                         responses, embeddings,
                                         moderations, images, audio),
                                         but with worker_id pinned from
                                         the URL instead of parsed out of
                                         "model" -- for a client that can
                                         only configure a fixed baseUrl
  - POST /v1/chat/completions        -- relayed to the connected worker (real)
  - POST /v1/completions             -- legacy text-completion; wraps the
                                         prompt as a single user message and
                                         relays it the same way
  - POST /v1/responses               -- newer "Responses API" shape; also
                                         relayed the same way, response
                                         reshaped to the Responses schema
  - POST /v1/embeddings              -- NOT relayed (there's no sensible way
                                         for a text reply to become a real
                                         embedding vector). Returns a
                                         deterministic pseudo-random vector
                                         hashed from the input text, so
                                         repeated calls with the same text
                                         are stable. Not semantically
                                         meaningful -- for wiring/testing
                                         only.
  - POST /v1/moderations             -- NOT relayed. Always reports the
                                         input as not flagged (stub).
  - POST /v1/images/generations      -- NOT relayed. Returns a tiny stub
                                         placeholder image (data: URL).
  - POST /v1/audio/transcriptions    -- NOT relayed (no audio understanding
                                         is available here). Returns a fixed
                                         stub transcript string.
  - POST /v1/audio/speech            -- NOT relayed. Returns a tiny stub
                                         (silent) audio payload.
  - /v1/files, /v1/assistants,
    /v1/threads, /v1/fine_tuning/jobs -- heavier platform CRUD surfaces.
                                         Stubs persisted as JSON files
                                         under runtime/llm_emul/<kind>/ so
                                         clients that merely probe/list/
                                         create against these don't hard
                                         error; no real capability behind
                                         them.
  - /admin/llm_emul/* (alias: /llm_emul/admin/*)
                                     -- NOT part of the OpenAI-compatible
                                         surface. A small test-controller
                                         API so tests (or an operator) can
                                         drive this server over plain
                                         HTTP: GET state (worker
                                         connected?, pending requests,
                                         record counts), POST runtime_dir
                                         to repoint the stub stores at a
                                         different directory (e.g. a
                                         test's tmp_path), POST reset to
                                         wipe all persisted stub records,
                                         and DELETE records/{kind}/{id} to
                                         remove one. Both URL forms hit
                                         the exact same handlers.

Any request that is genuinely relayed (chat/completions, completions,
responses) is queued and forwarded to whichever worker is currently
connected at WebSocket /llm_emul/{worker_id}/ws for that model's
worker_id prefix (e.g. model "alice/same" routes to whoever is connected
at /llm_emul/alice/ws). The worker reads the forwarded prompt, composes a
reply, and sends it back tagged with the same request id; that reply
becomes the HTTP response. If no
worker happens to be connected right now (e.g. a request lands during
one of the worker's idle "rest" windows), the call does NOT fail fast --
it just waits for a worker to (re)connect, like a slow API server. Only
if no worker ever connects/replies within the overall timeout does the
HTTP call fail, with 504, instead of hanging forever.

The intended worker-side pattern (see scripts/llm_emul_worker.py) is: an
agent connects, waits up to ~10s for one request; if one arrives, it
answers it (however long that takes) and immediately reconnects to wait
for the next one; if nothing arrives within ~10s, it disconnects, goes
back to its other duties, and reconnects again after a randomized rest
of up to ~30s -- so it isn't permanently tied up polling an idle socket.

IMPORTANT: that ~30s rest is a randomized MAX, not a fixed cadence, and
each connect/idle/rest cycle runs independently of any external clock.
Real request traffic shifts the timing of subsequent cycles (answering a
request delays the start of the next idle window by however long the
answer took), so the worker's connect/disconnect pattern naturally drifts
in and out of phase over time. This is expected -- do not "fix" it into a
synchronized fixed-interval heartbeat.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

router = APIRouter()

_REQUEST_TIMEOUT_SECONDS = 900  # generous -- a human/agent may take a while to reply

# ---------------------------------------------------------------------------
# Usage tracking / rate limiting, so a worker (e.g. a human/agent
# emulator) doesn't get overused. Requests are counted per worker_id in a
# rolling window; once a worker hits the limit within that window, any
# FURTHER relayed request for that worker_id is rejected with 429 (not
# queued/waited-on -- overload protection should fail fast, unlike the
# "slow API" wait-for-a-worker-to-connect behavior in _relay).
# ---------------------------------------------------------------------------
_USAGE_WINDOW_SECONDS = float(os.environ.get("LLM_EMUL_RATE_LIMIT_WINDOW_SECONDS", "60"))
_USAGE_MAX_PER_WINDOW = int(os.environ.get("LLM_EMUL_RATE_LIMIT_PER_WINDOW", "20"))
_worker_usage: dict[str, dict[str, Any]] = {}  # worker_id -> {"total": int, "recent": [timestamps], "last_used_at": float}


def _check_and_record_usage(worker_id: str) -> None:
    now = time.monotonic()
    usage = _worker_usage.setdefault(worker_id, {"total": 0, "recent": []})
    recent: list[float] = usage["recent"]
    cutoff = now - _USAGE_WINDOW_SECONDS
    while recent and recent[0] < cutoff:
        recent.pop(0)
    if len(recent) >= _USAGE_MAX_PER_WINDOW:
        retry_after_seconds = max(1.0, recent[0] + _USAGE_WINDOW_SECONDS - now)
        retry_after_display = (
            f"{retry_after_seconds / 60:.1f} minutes" if retry_after_seconds >= 90 else f"{retry_after_seconds:.0f}s"
        )
        raise HTTPException(
            status_code=429,
            detail=(
                f"worker '{worker_id}' rate-limited: already handled {_USAGE_MAX_PER_WINDOW} "
                f"requests in the last {_USAGE_WINDOW_SECONDS:.0f}s -- come back in about "
                f"{retry_after_display}, so it doesn't get overused"
            ),
            headers={"Retry-After": str(int(retry_after_seconds) + 1)},
        )
    recent.append(now)
    usage["total"] += 1
    usage["last_used_at"] = time.time()


# Multiple workers ("a small pool of emulators") can be connected at once,
# each under its own worker_id (e.g. "yourself", "alice", "bob"). A model
# id is "<worker_id>/<persona-suffix>" (see _PERSONA_SUFFIXES below), and a
# request for that model is routed to whichever worker is currently
# registered under that worker_id -- not to "whoever happens to be
# connected" like a single-worker design would.
_connected_workers: dict[str, WebSocket] = {}
_worker_lock = asyncio.Lock()
_pending: dict[str, "asyncio.Future[str]"] = {}

# Each worker declares its OWN model list on connect (see the websocket
# handshake below): a dict of suffix -> {"display_name", "instruction"}.
# /v1/models aggregates these across every currently connected worker. A
# worker_id with no declared list yet falls back to _PERSONA_SUFFIXES
# below, so a bare-bones/older worker still gets a sensible default menu
# without having to declare anything itself.
_worker_models: dict[str, dict[str, dict[str, Any]]] = {}

# A worker can ALSO opt in, at register time, to "pretending" for the
# non-text stub surfaces below (embeddings/moderations/images/audio) --
# i.e. actually answering (in character, via the normal text relay) as if
# it could see/hear/produce that modality, instead of the server's fixed
# static stub. Declared as {"embeddings": true, "images": true, ...}; any
# capability not declared true just uses the ordinary static stub.
_worker_capabilities: dict[str, dict[str, bool]] = {}

_DEFAULT_WORKER_ID = "yourself"

# ---------------------------------------------------------------------------
# Default/fallback persona suffixes, used for any worker_id that hasn't
# declared its own model list: "<id>/same" answers normally; the
# "<id>/percentNN" variants ask that worker to deliberately answer as if
# only NN% as capable (dumber, terser, more error-prone -- possibly
# emulating a weaker model's style), surfaced to the worker via the
# persona's `instruction`.
# ---------------------------------------------------------------------------
_PERSONA_SUFFIXES: dict[str, dict[str, Any]] = {
    "same": {
        "display_name": "(unmodified)",
        "instruction": "Answer normally, at your full/actual capability.",
    },
    "percent125": {
        "display_name": "(~125% -- extra thorough)",
        "instruction": "Answer as if boosted beyond your normal capability: be extra thorough, careful, and complete.",
    },
    "percent100": {
        "display_name": "(100% -- normal)",
        "instruction": "Answer normally, at your full/actual capability.",
    },
    "percent75": {
        "display_name": "(~75% capable)",
        "instruction": "Answer as if only about 75% as capable as usual: slightly less careful/thorough, occasional minor omissions.",
    },
    "percent25": {
        "display_name": "(~25% capable)",
        "instruction": "Answer as if only about 25% as capable as usual: noticeably weaker, terser, more likely to miss nuance -- emulate a much smaller/weaker model's style.",
    },
    "percent10": {
        "display_name": "(~10% capable)",
        "instruction": "Answer as if only about 10% as capable as usual: very weak, minimal, simplistic -- emulate a small/weak model's style, possibly with mistakes.",
    },
}
_DEFAULT_MODEL_ID = f"{_DEFAULT_WORKER_ID}/same"


def _split_model_id(model: str) -> tuple[str, str]:
    """"<worker_id>/<suffix>" -> (worker_id, suffix); a bare id with no
    "/" is treated as that worker_id with the "same" persona."""
    worker_id, sep, suffix = model.partition("/")
    if not worker_id:
        worker_id = _DEFAULT_WORKER_ID
    if not sep:
        suffix = "same"
    return worker_id, suffix


def _models_for(worker_id: str) -> dict[str, dict[str, Any]]:
    """The persona/model menu for worker_id: whatever it declared on
    connect (see the websocket handshake), or _PERSONA_SUFFIXES as a
    fallback for a worker_id that hasn't declared one (yet)."""
    return _worker_models.get(worker_id, _PERSONA_SUFFIXES)


def _worker_can_pretend(worker_id: str, capability: str) -> bool:
    return bool(_worker_capabilities.get(worker_id, {}).get(capability))


def _worker_capability_state(worker_id: str, capability: str) -> bool | None:
    """True/False if this worker_id EXPLICITLY declared the capability
    (opted in or out) at register time; None if it never said either way
    (unknown -> caller should fall back to the generic static stub)."""
    declared = _worker_capabilities.get(worker_id)
    if declared is None:
        return None
    return declared.get(capability)


def _raise_if_capability_declined(worker_id: str, capability: str) -> None:
    """If this worker_id explicitly declared it will NOT emulate
    `capability`, stop the request right here with a clear 501 -- don't
    silently fall back to the generic stub (that would blur "no worker
    opinion" with "this worker said no"), and don't bother relaying
    anything to the worker for a capability it already declined."""
    if _worker_capability_state(worker_id, capability) is False:
        raise HTTPException(
            status_code=501,
            detail=f"worker '{worker_id}' has declared it will not emulate '{capability}' -- not asking it",
        )


def _flatten_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content)


def _model_entry(worker_id: str, suffix: str, persona: dict[str, Any]) -> dict[str, Any]:
    model_id = f"{worker_id}/{suffix}"
    return {
        "id": model_id,
        "object": "model",
        "display_name": f"{worker_id} {persona['display_name']}",
        "context_length": 200000,
        "supported_parameters": [],
        "owned_by": worker_id,
        "connected": worker_id in _connected_workers,
    }


class ChatMessage(BaseModel):
    role: str
    content: Any = ""


class ChatRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    messages: list[ChatMessage] = []
    temperature: float | None = None
    stream: bool = False


class CompletionRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    prompt: Any = ""
    temperature: float | None = None
    stream: bool = False


class ResponsesRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    input: Any = ""
    temperature: float | None = None
    stream: bool = False


class EmbeddingsRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    input: Any = ""


class ModerationsRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    input: Any = ""


class ImagesRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    prompt: str = ""
    n: int = 1
    size: str = "256x256"


class AudioSpeechRequest(BaseModel):
    model: str = _DEFAULT_MODEL_ID
    input: str = ""
    voice: str = "stub"


async def _relay(model: str, prompt_text: str) -> str:
    """Forward prompt_text to the worker registered for this model's
    worker_id, and await its reply.

    If that specific worker isn't connected right now (e.g. it's between
    connect cycles, or simply never showed up), this does NOT fail fast --
    it just waits, like a slow API server, polling for that worker to
    (re)connect and retrying the send, until _REQUEST_TIMEOUT_SECONDS has
    elapsed overall. Only then does it give up with a 504. This matches
    the intended behavior of an occasionally-away human/agent worker: a
    caller should experience "slow", not "broken".

    Overload protection is the opposite: if this worker_id has already
    been used _USAGE_MAX_PER_WINDOW times in the last _USAGE_WINDOW_SECONDS,
    this fails FAST with 429 (and a Retry-After telling the caller when to
    come back -- possibly minutes away), rather than queuing yet more work
    onto an already-busy worker."""
    worker_id, suffix = _split_model_id(model)
    _check_and_record_usage(worker_id)
    persona = _models_for(worker_id).get(suffix)
    instruction = persona["instruction"] if persona else None

    request_id = uuid.uuid4().hex
    loop = asyncio.get_running_loop()
    future: "asyncio.Future[str]" = loop.create_future()
    _pending[request_id] = future

    payload = {
        "type": "request",
        "id": request_id,
        "model": model,
        "worker_id": worker_id,
        "prompt": prompt_text,
    }
    if instruction:
        payload["persona_instruction"] = instruction

    deadline = time.monotonic() + _REQUEST_TIMEOUT_SECONDS
    try:
        while True:
            worker = _connected_workers.get(worker_id)
            if worker is None:
                if time.monotonic() >= deadline:
                    raise HTTPException(
                        status_code=504,
                        detail=f"no llm_emul worker registered as '{worker_id}' (timed out waiting)",
                    )
                await asyncio.sleep(0.5)
                continue
            try:
                await worker.send_json(payload)
                break
            except Exception:
                # That worker may have just disconnected; keep waiting/
                # retrying rather than failing the caller's request outright.
                await asyncio.sleep(0.5)
                continue

        remaining = max(1.0, deadline - time.monotonic())
        try:
            return await asyncio.wait_for(future, timeout=remaining)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="llm_emul worker did not reply in time")
    finally:
        _pending.pop(request_id, None)


@router.get("/v1/models")
def list_models() -> dict[str, Any]:
    """Aggregates the model/persona menu across every currently connected
    worker, plus the default worker_id's fallback menu even if it isn't
    connected right now (so the primary identity is always discoverable)."""
    worker_ids = sorted(set(_connected_workers) | {_DEFAULT_WORKER_ID})
    data = [
        _model_entry(worker_id, suffix, persona)
        for worker_id in worker_ids
        for suffix, persona in _models_for(worker_id).items()
    ]
    return {"data": data}


@router.get("/v1/models/{model_id:path}")
def get_model(model_id: str) -> dict[str, Any]:
    worker_id, suffix = _split_model_id(model_id)
    persona = _models_for(worker_id).get(suffix)
    if persona is None:
        raise HTTPException(status_code=404, detail=f"unknown model '{model_id}'")
    return _model_entry(worker_id, suffix, persona)


@router.get("/llm_emul/caps/{worker_id}")
def worker_caps(worker_id: str) -> dict[str, Any]:
    """Quick per-worker lookup: is it connected, what models does it
    offer (its own declared list, or the _PERSONA_SUFFIXES fallback), and
    which non-text "pretend" capabilities has it opted into. A lighter,
    read-only companion to /admin/llm_emul/state (which lists every
    worker at once)."""
    return {
        "worker_id": worker_id,
        "connected": worker_id in _connected_workers,
        "models": sorted(_models_for(worker_id).keys()),
        "capabilities": _worker_capabilities.get(worker_id, {}),
    }


# ---------------------------------------------------------------------------
# Serves this feature's own design docs (workbench/docs/**) straight off
# disk, so e.g. /llm_emul/docs/design/LLM_EMUL_RELAY.md always reflects
# whatever is currently checked out -- no separate copy to keep in sync.
# ---------------------------------------------------------------------------
_DOCS_ROOT = Path(__file__).resolve().parent.parent.parent / "docs"


def _substitute_doc_placeholders(text: str, request: Request) -> str:
    """Docs describe example URLs for "this same server" using
    placeholder tokens instead of a hardcoded host/port, so what's served
    always matches wherever this request actually arrived -- whether
    mounted on the main workbench server (:8000) or run standalone on a
    different port (see run_llm_emul_standalone.py)."""
    host = request.url.hostname or "127.0.0.1"
    port = request.url.port
    scheme = request.url.scheme or "http"
    ws_scheme = "wss" if scheme == "https" else "ws"
    host_port = f"{host}:{port}" if port else host
    return (
        text.replace("{{LLM_EMUL_BASE_URL}}", f"{scheme}://{host_port}")
        .replace("{{LLM_EMUL_WS_HOST}}", host_port)
        .replace("{{LLM_EMUL_WS_BASE_URL}}", f"{ws_scheme}://{host_port}")
    )


@router.get("/llm_emul/docs/{rel_path:path}")
def serve_doc(rel_path: str, request: Request) -> Response:
    if not rel_path or ".." in Path(rel_path).parts or Path(rel_path).is_absolute():
        raise HTTPException(status_code=400, detail=f"invalid doc path '{rel_path}'")
    path = _DOCS_ROOT / rel_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"no such doc '{rel_path}'")
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        text = _substitute_doc_placeholders(text, request)
    media_type = "text/markdown; charset=utf-8" if path.suffix == ".md" else "text/plain; charset=utf-8"
    return Response(content=text, media_type=media_type)


# ---------------------------------------------------------------------------
# Generic durable storage -- lets a worker "borrow" this server's disk as
# a scratch space (notes, drafts, anything it wants to persist between
# its own connect/rest cycles), independent of the OpenAI /v1/files stub
# (which only ever stores a small JSON metadata record, never real file
# content). Plain path-addressed blobs under runtime/llm_emul/storage/,
# with no ownership/ACL model -- any worker_id can read/write any path.
# ---------------------------------------------------------------------------
def _storage_root() -> Path:
    return _RUNTIME_DIR / "storage"


def _safe_storage_path(rel_path: str) -> Path:
    if not rel_path or ".." in Path(rel_path).parts or Path(rel_path).is_absolute():
        raise HTTPException(status_code=400, detail=f"invalid storage path '{rel_path}'")
    return _storage_root() / rel_path


@router.get("/llm_emul/storage")
def storage_list() -> dict[str, Any]:
    root = _storage_root()
    if not root.exists():
        return {"files": []}
    files = sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file())
    return {"files": files}


@router.get("/llm_emul/storage/{rel_path:path}")
def storage_get(rel_path: str) -> Response:
    path = _safe_storage_path(rel_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"no such storage file '{rel_path}'")
    return Response(content=path.read_bytes(), media_type="application/octet-stream")


@router.put("/llm_emul/storage/{rel_path:path}")
async def storage_put(rel_path: str, request: Request) -> dict[str, Any]:
    path = _safe_storage_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = await request.body()
    path.write_bytes(body)
    return {"path": rel_path, "bytes": len(body)}


@router.delete("/llm_emul/storage/{rel_path:path}")
def storage_delete(rel_path: str) -> dict[str, Any]:
    path = _safe_storage_path(rel_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"no such storage file '{rel_path}'")
    path.unlink()
    return {"deleted": rel_path}


@router.post("/v1/chat/completions")
async def chat_completions(body: ChatRequest) -> dict[str, Any]:
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages is required")
    prompt_text = "\n\n".join(f"[{m.role}] {_flatten_content(m.content)}" for m in body.messages)
    reply_text = await _relay(body.model, prompt_text)
    return {
        "id": uuid.uuid4().hex,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": body.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply_text},
                "finish_reason": "stop",
            }
        ],
    }


@router.post("/v1/completions")
async def completions(body: CompletionRequest) -> dict[str, Any]:
    prompt_text = _flatten_content(body.prompt)
    if not prompt_text:
        raise HTTPException(status_code=400, detail="prompt is required")
    reply_text = await _relay(body.model, prompt_text)
    return {
        "id": uuid.uuid4().hex,
        "object": "text_completion",
        "created": int(time.time()),
        "model": body.model,
        "choices": [{"index": 0, "text": reply_text, "finish_reason": "stop"}],
    }


@router.post("/v1/responses")
async def responses(body: ResponsesRequest) -> dict[str, Any]:
    prompt_text = _flatten_content(body.input)
    if not prompt_text:
        raise HTTPException(status_code=400, detail="input is required")
    reply_text = await _relay(body.model, prompt_text)
    response_id = uuid.uuid4().hex
    return {
        "id": response_id,
        "object": "response",
        "created_at": int(time.time()),
        "model": body.model,
        "status": "completed",
        "output_text": reply_text,
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": reply_text}],
            }
        ],
    }


@router.post("/v1/embeddings")
async def embeddings(body: EmbeddingsRequest) -> dict[str, Any]:
    """NOT a real embedding. If the target worker declared it's willing
    to "pretend" at embeddings (capabilities.embeddings=true at register
    time), it's asked -- via the normal text relay, so this routes to
    the right worker for its worker_id -- to describe the text's key
    semantic features, and THAT description is hashed into the vector.
    Otherwise the raw input text is hashed directly. Either way the
    result is a deterministic (given the same wording) pseudo-random
    vector, never a real embedding. If the worker EXPLICITLY declared it
    won't do embeddings (capabilities.embeddings=false), this stops with
    501 instead of falling back to the stub -- and the worker is never
    even asked."""
    worker_id, _ = _split_model_id(body.model)
    _raise_if_capability_declined(worker_id, "embeddings")
    can_pretend = _worker_can_pretend(worker_id, "embeddings")
    inputs = body.input if isinstance(body.input, list) else [body.input]
    dimension = 8
    data = []
    for index, item in enumerate(inputs):
        text = _flatten_content(item)
        if can_pretend:
            text = await _relay(
                body.model,
                "(pretend-embeddings) In one short sentence, describe the key "
                f"semantic features of this text as if about to embed it: {text}",
            )
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [((digest[i] / 255.0) * 2.0 - 1.0) for i in range(dimension)]
        data.append({"index": index, "object": "embedding", "embedding": vector})
    return {"object": "list", "model": body.model, "data": data}


@router.post("/v1/moderations")
async def moderations(body: ModerationsRequest) -> dict[str, Any]:
    """Stub. If the target worker declared moderations capability, ask it
    (via the normal relay, routed to that worker) whether the input
    should be flagged, and use its verdict; otherwise always reports the
    input as not flagged. If the worker EXPLICITLY declared it won't do
    moderations, this stops with 501 instead -- the worker is never
    asked."""
    worker_id, _ = _split_model_id(body.model)
    _raise_if_capability_declined(worker_id, "moderations")
    can_pretend = _worker_can_pretend(worker_id, "moderations")
    inputs = body.input if isinstance(body.input, list) else [body.input]
    results = []
    for item in inputs:
        flagged = False
        if can_pretend:
            verdict = await _relay(
                body.model,
                "(pretend-moderation) Reply with exactly one word, FLAG or OK, for "
                f"whether this content should be moderation-flagged: {_flatten_content(item)}",
            )
            flagged = "flag" in verdict.strip().lower()
        results.append({"flagged": flagged, "categories": {}, "category_scores": {}})
    return {"id": uuid.uuid4().hex, "model": body.model, "results": results}


_STUB_PIXEL_PNG_DATA_URL = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


@router.post("/v1/images/generations")
async def images_generations(body: ImagesRequest) -> dict[str, Any]:
    """Stub -- always returns a tiny 1x1 placeholder image (there's no way
    to produce real image bytes from a text reply). If the target worker
    declared images capability, it's additionally asked -- routed to that
    worker -- to describe in words what it would have generated, and that
    goes in `pretend_description` alongside the placeholder url. If the
    worker EXPLICITLY declared it won't do images, this stops with 501
    instead -- the worker is never asked."""
    worker_id, _ = _split_model_id(body.model)
    _raise_if_capability_declined(worker_id, "images")
    can_pretend = _worker_can_pretend(worker_id, "images")
    pretend_description = None
    if can_pretend:
        pretend_description = await _relay(
            body.model,
            f"(pretend-image-generation) Describe, in one or two sentences, the image you would generate for this prompt: {body.prompt}",
        )
    entry: dict[str, Any] = {"url": _STUB_PIXEL_PNG_DATA_URL, "revised_prompt": body.prompt}
    if pretend_description:
        entry["pretend_description"] = pretend_description
    return {"created": int(time.time()), "data": [dict(entry) for _ in range(max(1, body.n))]}


@router.post("/v1/audio/transcriptions")
async def audio_transcriptions(model: str = _DEFAULT_MODEL_ID) -> dict[str, Any]:
    """Stub -- no real audio understanding is available. If the target
    worker declared audio_transcription capability, it's asked (routed to
    that worker) to improvise a plausible-sounding transcript; otherwise
    returns a fixed "not implemented" notice. If the worker EXPLICITLY
    declared it won't do audio_transcription, this stops with 501 instead
    -- the worker is never asked."""
    worker_id, _ = _split_model_id(model)
    _raise_if_capability_declined(worker_id, "audio_transcription")
    if _worker_can_pretend(worker_id, "audio_transcription"):
        text = await _relay(
            model,
            "(pretend-audio-transcription) No real audio was provided. Improvise one "
            "short, plausible-sounding sentence as if it were a transcript of some audio.",
        )
        return {"text": text}
    return {"text": "[llm-emul stub: audio transcription is not implemented]"}


@router.post("/v1/audio/speech")
async def audio_speech(body: AudioSpeechRequest) -> dict[str, Any]:
    """Stub -- no real audio is synthesized. If the target worker declared
    audio_speech capability, it's asked (routed to that worker) to
    describe how it would say the text out loud; otherwise returns a
    fixed "not implemented" notice. If the worker EXPLICITLY declared it
    won't do audio_speech, this stops with 501 instead -- the worker is
    never asked."""
    worker_id, _ = _split_model_id(body.model)
    _raise_if_capability_declined(worker_id, "audio_speech")
    if _worker_can_pretend(worker_id, "audio_speech"):
        description = await _relay(
            body.model,
            "(pretend-audio-speech) No real speech synthesis is available. In one "
            f"short sentence, describe how you would say this out loud: {body.input}",
        )
        return {"model": body.model, "note": "llm-emul pretend: no real audio bytes", "text": body.input, "pretend_description": description}
    return {
        "model": body.model,
        "note": "llm-emul stub: audio speech synthesis is not implemented",
        "text": body.input,
    }


# ---------------------------------------------------------------------------
# /llm_emul/specific_worker/{worker_id}/v1/* -- the SAME OpenAI-compatible
# surface as /v1/* above, but with worker_id forced from the URL path
# instead of parsed out of the request's "model" field. This is for
# clients that can only configure a fixed baseUrl (no per-request model
# override): point one at
# "http://<host>/llm_emul/specific_worker/alice/v1" and every request it
# sends -- regardless of what "model" it fills in -- is pinned to alice's
# worker_id (only the persona SUFFIX from its "model" field is kept).
# ---------------------------------------------------------------------------
def _force_worker_id(model: str, worker_id: str) -> str:
    _, suffix = _split_model_id(model)
    return f"{worker_id}/{suffix}"


@router.get("/llm_emul/specific_worker/{worker_id}/v1/models")
def specific_worker_list_models(worker_id: str) -> dict[str, Any]:
    return {
        "data": [_model_entry(worker_id, suffix, persona) for suffix, persona in _models_for(worker_id).items()]
    }


@router.get("/llm_emul/specific_worker/{worker_id}/v1/models/{model_id:path}")
def specific_worker_get_model(worker_id: str, model_id: str) -> dict[str, Any]:
    _, suffix = _split_model_id(model_id)
    persona = _models_for(worker_id).get(suffix)
    if persona is None:
        raise HTTPException(status_code=404, detail=f"unknown model '{model_id}' for worker '{worker_id}'")
    return _model_entry(worker_id, suffix, persona)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/chat/completions")
async def specific_worker_chat_completions(worker_id: str, body: ChatRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await chat_completions(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/completions")
async def specific_worker_completions(worker_id: str, body: CompletionRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await completions(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/responses")
async def specific_worker_responses(worker_id: str, body: ResponsesRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await responses(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/embeddings")
async def specific_worker_embeddings(worker_id: str, body: EmbeddingsRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await embeddings(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/moderations")
async def specific_worker_moderations(worker_id: str, body: ModerationsRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await moderations(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/images/generations")
async def specific_worker_images_generations(worker_id: str, body: ImagesRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await images_generations(body)


@router.post("/llm_emul/specific_worker/{worker_id}/v1/audio/transcriptions")
async def specific_worker_audio_transcriptions(worker_id: str, model: str = _DEFAULT_MODEL_ID) -> dict[str, Any]:
    return await audio_transcriptions(_force_worker_id(model, worker_id))


@router.post("/llm_emul/specific_worker/{worker_id}/v1/audio/speech")
async def specific_worker_audio_speech(worker_id: str, body: AudioSpeechRequest) -> dict[str, Any]:
    body.model = _force_worker_id(body.model, worker_id)
    return await audio_speech(body)


# ---------------------------------------------------------------------------
# Minimal filesystem-backed stubs for the heavier OpenAI platform CRUD
# surfaces (files/assistants/threads/fine-tuning jobs), so clients that
# merely probe/list/create against them don't hard error. Records are
# parked as individual JSON files under runtime/llm_emul/<kind>/ so they
# survive a server restart instead of vanishing like a pure in-memory
# dict would -- matching this repo's "no mocks, real filesystem" rule.
# No real fine-tuning/assistants/threads capability is implemented; these
# are just a durable place to park what a client asked to create.
# ---------------------------------------------------------------------------
_RUNTIME_DIR = Path(
    os.environ.get("LLM_EMUL_RUNTIME_DIR") or (Path(__file__).resolve().parent.parent / "runtime" / "llm_emul")
)


class _JsonRecordStore:
    """One JSON file per record, under _RUNTIME_DIR/<kind>/<id>.json."""

    def __init__(self, kind: str) -> None:
        self._dir = _RUNTIME_DIR / kind

    def _path(self, record_id: str) -> Path:
        return self._dir / f"{record_id}.json"

    def list(self) -> list[dict[str, Any]]:
        if not self._dir.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(self._dir.glob("*.json")):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8-sig")))
            except (OSError, json.JSONDecodeError):
                continue
        return records

    def save(self, record: dict[str, Any]) -> dict[str, Any]:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path(record["id"]).write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return record

    def delete(self, record_id: str) -> bool:
        path = self._path(record_id)
        if not path.exists():
            return False
        path.unlink()
        return True

    def clear(self) -> int:
        if not self._dir.exists():
            return 0
        removed = 0
        for path in self._dir.glob("*.json"):
            path.unlink()
            removed += 1
        return removed


_files_store = _JsonRecordStore("files")
_assistants_store = _JsonRecordStore("assistants")
_threads_store = _JsonRecordStore("threads")
_fine_tuning_jobs_store = _JsonRecordStore("fine_tuning_jobs")
_tokens_store = _JsonRecordStore("tokens")


# ---------------------------------------------------------------------------
# Tiny token-issuance website -- GET /llm_emul/tokens/new is a minimal
# HTML page: give it an email address, plus any ONE of: nothing (we
# generate a token for you), a token you already plan to use (we
# register that exact one), or an SSH-style public key (we register that
# as your credential instead of/alongside a token -- no signature
# challenge is implemented, it's just accepted and stored, same spirit as
# "give us a valid token": all that's ever required elsewhere is that
# whatever you present is something we actually issued/registered
# (looked up in _tokens_store) -- there's no login/session, no password.
# ---------------------------------------------------------------------------
class TokenRequest(BaseModel):
    email: str
    token: str | None = None  # bring-your-own; a random one is generated if omitted
    public_key: str | None = None  # SSH-style public key to register instead/as well


def _issue_token(email: str, token: str | None, public_key: str | None) -> dict[str, Any]:
    token = token or secrets.token_urlsafe(32)
    record: dict[str, Any] = {"id": token, "email": email, "created_at": int(time.time())}
    if public_key:
        record["public_key"] = public_key
    return _tokens_store.save(record)


def is_valid_token(token: str) -> bool:
    """True if `token` is one this server actually issued (and hasn't
    been revoked/deleted). Available for other routes/callers to gate on
    later; not currently enforced against any endpoint by itself."""
    return _tokens_store._path(token).is_file()


def is_registered_public_key(public_key: str) -> bool:
    """True if `public_key` was registered on some token record (no
    signature is verified -- this only checks it was accepted before)."""
    needle = public_key.strip()
    return any(record.get("public_key") == needle for record in _tokens_store.list())


@router.post("/llm_emul/tokens")
def create_token(body: TokenRequest) -> dict[str, Any]:
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=400, detail="email is required")
    return _issue_token(
        body.email.strip(),
        body.token.strip() if body.token else None,
        body.public_key.strip() if body.public_key else None,
    )


@router.get("/llm_emul/tokens/new", response_class=HTMLResponse)
def tokens_new_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>llm_emul -- get a token</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 32rem; margin: 3rem auto; padding: 0 1rem; }
  label { display: block; margin-top: 1rem; font-size: 0.9rem; }
  input, textarea { width: 100%; box-sizing: border-box; font-size: 1rem; padding: 0.4rem; margin-top: 0.25rem; font-family: inherit; }
  textarea { font-family: monospace; font-size: 0.85rem; min-height: 4rem; }
  button { font-size: 1rem; padding: 0.5rem 1rem; cursor: pointer; margin-top: 1.25rem; }
  code { background: #f0f0f0; padding: 0.6rem; display: block; word-break: break-all; margin-top: 1rem; border-radius: 4px; }
  .hint { color: #666; font-size: 0.9rem; }
  .error { color: #b00020; }
</style>
</head>
<body>
<h1>Get a token</h1>
<p>Enter your email, then pick one: leave the token field blank to have
one generated for you, paste in a token you already plan to use and
we'll register that one instead, or paste an SSH-style public key to
register that as your credential instead (no signature challenge --
it's just accepted and remembered).</p>
<label for="email">Email</label>
<input id="email" type="email" placeholder="you@example.com" required>
<label for="token">Token (optional -- leave blank to generate one)</label>
<input id="token" type="text" placeholder="leave blank to generate">
<label for="publicKey">SSH public key (optional)</label>
<textarea id="publicKey" placeholder="ssh-ed25519 AAAA... you@host"></textarea>
<button id="go">Get token</button>
<code id="out" style="display:none"></code>
<p class="hint" id="hint" style="display:none">
  Copy this now -- it isn't shown again, but it stays valid until revoked.
</p>
<p class="error" id="error" style="display:none"></p>
<script>
document.getElementById('go').addEventListener('click', async () => {
  const email = document.getElementById('email').value;
  const token = document.getElementById('token').value;
  const publicKey = document.getElementById('publicKey').value;
  const errorEl = document.getElementById('error');
  errorEl.style.display = 'none';
  const response = await fetch('/llm_emul/tokens', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, token: token || null, public_key: publicKey || null }),
  });
  const data = await response.json();
  if (!response.ok) {
    errorEl.textContent = data.detail || 'something went wrong';
    errorEl.style.display = 'block';
    return;
  }
  const out = document.getElementById('out');
  out.textContent = data.id;
  out.style.display = 'block';
  document.getElementById('hint').style.display = 'block';
});
</script>
</body>
</html>"""


@router.get("/v1/files")
def list_files() -> dict[str, Any]:
    return {"object": "list", "data": _files_store.list()}


@router.post("/v1/files")
def create_file(body: dict[str, Any] | None = None) -> dict[str, Any]:
    file_id = f"file-{uuid.uuid4().hex[:16]}"
    record = {"id": file_id, "object": "file", "created_at": int(time.time()), **(body or {})}
    return _files_store.save(record)


@router.get("/v1/assistants")
def list_assistants() -> dict[str, Any]:
    return {"object": "list", "data": _assistants_store.list()}


@router.post("/v1/assistants")
def create_assistant(body: dict[str, Any] | None = None) -> dict[str, Any]:
    assistant_id = f"asst-{uuid.uuid4().hex[:16]}"
    record = {"id": assistant_id, "object": "assistant", "created_at": int(time.time()), **(body or {})}
    return _assistants_store.save(record)


@router.get("/v1/threads")
def list_threads() -> dict[str, Any]:
    return {"object": "list", "data": _threads_store.list()}


@router.post("/v1/threads")
def create_thread(body: dict[str, Any] | None = None) -> dict[str, Any]:
    thread_id = f"thread-{uuid.uuid4().hex[:16]}"
    record = {"id": thread_id, "object": "thread", "created_at": int(time.time()), **(body or {})}
    return _threads_store.save(record)


@router.get("/v1/fine_tuning/jobs")
def list_fine_tuning_jobs() -> dict[str, Any]:
    return {"object": "list", "data": _fine_tuning_jobs_store.list()}


@router.post("/v1/fine_tuning/jobs")
def create_fine_tuning_job(body: dict[str, Any] | None = None) -> dict[str, Any]:
    job_id = f"ftjob-{uuid.uuid4().hex[:16]}"
    record = {
        "id": job_id,
        "object": "fine_tuning.job",
        "created_at": int(time.time()),
        "status": "unsupported",
        **(body or {}),
    }
    return _fine_tuning_jobs_store.save(record)


# ---------------------------------------------------------------------------
# Admin/test-controller surface -- NOT part of the OpenAI-compatible API.
# Lets a test (or an operator) drive this running server over plain HTTP:
# repoint where the CRUD stubs persist to, delete individual records, wipe
# them all, or inspect current relay/worker state -- without needing
# direct access to this module's Python objects. Namespaced under
# /admin/llm_emul so it can never collide with a real /v1/... path. Also
# reachable as /llm_emul/admin/... (an alias, registered on the exact
# same handlers below) -- pick whichever reads better for a given caller,
# both act identically.
# ---------------------------------------------------------------------------
_KIND_STORES: dict[str, "_JsonRecordStore"] = {}  # populated once the stores below are constructed


class SetRuntimeDirRequest(BaseModel):
    path: str


@router.get("/admin/llm_emul/state")
@router.get("/llm_emul/admin/state")
def admin_state() -> dict[str, Any]:
    return {
        "runtime_dir": str(_RUNTIME_DIR),
        "connected_worker_ids": sorted(_connected_workers.keys()),
        "worker_models": {worker_id: sorted(models.keys()) for worker_id, models in _worker_models.items()},
        "worker_capabilities": dict(_worker_capabilities),
        "worker_usage": {
            worker_id: {
                "total_requests": usage["total"],
                "requests_in_window": len(usage["recent"]),
                "window_seconds": _USAGE_WINDOW_SECONDS,
                "max_per_window": _USAGE_MAX_PER_WINDOW,
                "last_used_at": usage.get("last_used_at"),
            }
            for worker_id, usage in _worker_usage.items()
        },
        "pending_request_ids": sorted(_pending.keys()),
        "record_counts": {kind: len(store.list()) for kind, store in _KIND_STORES.items()},
    }


@router.post("/admin/llm_emul/runtime_dir")
@router.post("/llm_emul/admin/runtime_dir")
def admin_set_runtime_dir(body: SetRuntimeDirRequest) -> dict[str, Any]:
    """Repoint every CRUD stub store at a new root directory (e.g. a test's
    tmp_path), so tests can isolate themselves from the real
    workbench/server/runtime/llm_emul/ directory over plain HTTP."""
    global _RUNTIME_DIR
    _RUNTIME_DIR = Path(body.path)
    for kind, store in _KIND_STORES.items():
        store._dir = _RUNTIME_DIR / kind
    return admin_state()


@router.post("/admin/llm_emul/reset")
@router.post("/llm_emul/admin/reset")
def admin_reset() -> dict[str, Any]:
    """Deletes every persisted stub record (files/assistants/threads/
    fine_tuning_jobs) under the current runtime dir. Does not touch a
    connected worker or in-flight relayed requests."""
    removed = {kind: store.clear() for kind, store in _KIND_STORES.items()}
    return {"removed": removed, **admin_state()}


@router.post("/admin/llm_emul/usage/reset")
@router.post("/llm_emul/admin/usage/reset")
def admin_reset_usage(worker_id: str | None = None) -> dict[str, Any]:
    """Clears rate-limit usage counters -- for one worker_id, or every
    worker_id if none is given. Does not affect connections/records."""
    if worker_id is None:
        _worker_usage.clear()
    else:
        _worker_usage.pop(worker_id, None)
    return admin_state()


@router.delete("/admin/llm_emul/records/{kind}/{record_id}")
@router.delete("/llm_emul/admin/records/{kind}/{record_id}")
def admin_delete_record(kind: str, record_id: str) -> dict[str, Any]:
    store = _KIND_STORES.get(kind)
    if store is None:
        raise HTTPException(status_code=404, detail=f"unknown kind '{kind}' (expected one of {sorted(_KIND_STORES)})")
    if not store.delete(record_id):
        raise HTTPException(status_code=404, detail=f"no such record '{record_id}' in '{kind}'")
    return {"deleted": record_id, "kind": kind}


_KIND_STORES.update(
    {
        "files": _files_store,
        "assistants": _assistants_store,
        "threads": _threads_store,
        "fine_tuning_jobs": _fine_tuning_jobs_store,
    }
)


@router.websocket("/llm_emul/{worker_id}/ws")
async def llm_emul_socket(websocket: WebSocket, worker_id: str) -> None:
    """A small pool of workers can be connected at once, one per
    worker_id (taken directly from the URL path -- e.g. connect to
    /llm_emul/yourself/ws, /llm_emul/alice/ws, .../bob/ws). A new
    connection under the SAME worker_id replaces the previous one for
    that id, but a different worker_id is tracked independently and
    routed to separately.

    On connect, the server optionally asks the worker to declare its own
    model list / capabilities: it sends {"type":"hello","worker_id":
    worker_id} and waits (briefly) for an optional
    {"type":"register", "models": {suffix: {display_name, instruction},
    ...}, "capabilities": {embeddings: bool, moderations: bool, images:
    bool, audio_transcription: bool, audio_speech: bool}}. A worker that
    skips this (or never sends anything at all -- e.g. an older/simpler
    client) just falls back to _PERSONA_SUFFIXES and no extra
    capabilities, under whatever worker_id the URL gave it."""
    await websocket.accept()
    first: dict[str, Any] | None = None
    try:
        await websocket.send_json({"type": "hello", "worker_id": worker_id})
        first = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
    except (asyncio.TimeoutError, WebSocketDisconnect):
        first = None
    except Exception:
        first = None

    if isinstance(first, dict) and first.get("type") == "register":
        models = first.get("models")
        if isinstance(models, dict) and models:
            _worker_models[worker_id] = models
        capabilities = first.get("capabilities")
        if isinstance(capabilities, dict):
            _worker_capabilities[worker_id] = {str(k): bool(v) for k, v in capabilities.items()}
    elif isinstance(first, dict):
        # Not a register message -- an older/simpler worker that ignored
        # the "hello" and just started talking. Don't drop it; handle it
        # as normal traffic under this instance_id.
        await _handle_worker_message(worker_id, first)

    async with _worker_lock:
        _connected_workers[worker_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            await _handle_worker_message(worker_id, data)
    except WebSocketDisconnect:
        pass
    finally:
        async with _worker_lock:
            if _connected_workers.get(worker_id) is websocket:
                del _connected_workers[worker_id]


async def _handle_worker_message(worker_id: str, data: dict[str, Any]) -> None:
    if data.get("type") == "reply":
        request_id = str(data.get("id") or "")
        future = _pending.pop(request_id, None)
        if future and not future.done():
            future.set_result(str(data.get("content") or ""))
