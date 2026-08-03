from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_unsloth_provider_requires_studio_api_key() -> None:
    config = json.loads((ROOT / "config" / "llm_providers.json").read_text(encoding="utf-8"))
    unsloth = next(item for item in config["providers"] if item["id"] == "unsloth")

    assert unsloth["api_key_env"] == "ARC3_UNSLOTH_API_KEY"
    assert unsloth["api_key_optional"] is False
    assert unsloth["enabled"] == "auto"
    assert unsloth["base_url"].endswith("/v1")
    assert unsloth["health_url"].endswith("/api/health")
