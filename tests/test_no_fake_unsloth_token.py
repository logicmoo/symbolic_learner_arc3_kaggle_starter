from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_unsloth_does_not_use_optional_dummy_authentication() -> None:
    config = (ROOT / "config" / "llm_providers.json").read_text(encoding="utf-8")

    assert '"id": "unsloth"' in config
    assert '"api_key_optional": false' in config


def test_environment_example_never_recommends_local_no_key() -> None:
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    docs = (ROOT / "config" / "README.md").read_text(encoding="utf-8")

    assert "local-no-key" not in example
    assert "local-no-key" not in docs
    assert "sk-unsloth-" in example
