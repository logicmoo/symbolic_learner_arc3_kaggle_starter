"""Live diagnostic ping: ask several SNET-hosted models to describe themselves.

Skipped automatically when SNET_API_KEY is not set. Run with -s to see the
per-model latency and self-description responses:

    pytest tests/test_snet_model_ping.py -s
"""

from __future__ import annotations

import base64
import json
import os
import struct
import time
import urllib.error
import urllib.request
import zlib

import pytest

SNET_BASE_URL = "https://llm.c.singularitynet.io/v1"
SNET_MODELS = [
    "google/gemma-3-27b-it",
    "google/gemma-4-31b-it",
    "google/gemma-4-26b-a4b-it",
    "minimax/minimax-m3",
    "minimax/minimax-m3-f",
    "qwen/qwen3-32b",
    "qwen/qwen3.5-35b-a3b",
    "qwen/qwen3.8-27b",
]
PROMPT = "Describe yourself in 2-3 sentences. Who and what are you, and who built you?"
TIMEOUT_S = 60


def _post_chat(model: str, api_key: str, messages: list, max_tokens: int) -> dict:
    body = json.dumps(
        {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{SNET_BASE_URL}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MeTTaSymbolicLearnerWorkbench-ping/1.0",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload = json.loads(response.read().decode("utf-8"))
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        content = ((payload.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        return {"status": "ok", "latencyMs": latency_ms, "response": content.strip()}
    except urllib.error.HTTPError as error:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        detail = error.read().decode("utf-8", "replace")[:400]
        return {"status": f"HTTP {error.code}", "latencyMs": latency_ms, "response": detail}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {"status": "error", "latencyMs": latency_ms, "response": str(error)}


def _ping(model: str, api_key: str) -> dict:
    result = _post_chat(model, api_key, [{"role": "user", "content": PROMPT}], 200)
    return {"model": model, **result}


def _solid_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Encode a solid-color RGB PNG without any third-party imaging dependency."""
    red, green, blue = rgb
    row = bytes([0]) + bytes([red, green, blue]) * width  # filter byte 0 + RGB pixels
    raw = row * height

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (truecolor)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _blue_data_url() -> str:
    return "data:image/png;base64," + base64.b64encode(_solid_png(64, 64, (0, 0, 255))).decode("ascii")


def _ping_vision(model: str, api_key: str, data_url: str) -> dict:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this image? Reply with just the color name."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    result = _post_chat(model, api_key, messages, 60)
    return {"model": model, **result}


@pytest.mark.skipif(not os.environ.get("SNET_API_KEY"), reason="SNET_API_KEY is not set")
def test_snet_models_describe_themselves() -> None:
    api_key = os.environ["SNET_API_KEY"]
    results = [_ping(model, api_key) for model in SNET_MODELS]

    print("\n\n=== SNET model self-description ping ===")
    for item in results:
        print(f"\n--- {item['model']}  [{item['status']}, {item['latencyMs']} ms] ---")
        print(item["response"] or "(empty)")
    print("\n=== end ===\n")

    # Diagnostic ping: every target is attempted and returns a structured result.
    assert len(results) == len(SNET_MODELS)
    for item in results:
        assert {"model", "status", "latencyMs", "response"} <= set(item)


@pytest.mark.skipif(not os.environ.get("SNET_API_KEY"), reason="SNET_API_KEY is not set")
def test_snet_models_identify_blue_image() -> None:
    api_key = os.environ["SNET_API_KEY"]
    data_url = _blue_data_url()
    results = [_ping_vision(model, api_key, data_url) for model in SNET_MODELS]

    print("\n\n=== SNET solid-blue image color test ===")
    for item in results:
        print(f"\n--- {item['model']}  [{item['status']}, {item['latencyMs']} ms] ---")
        print(item["response"] or "(empty)")
    print("\n=== end ===\n")

    assert len(results) == len(SNET_MODELS)
    for item in results:
        assert {"model", "status", "latencyMs", "response"} <= set(item)

