from __future__ import annotations

import json
from types import SimpleNamespace

from multillm_runner import MultiLlmArc3Runner


def test_provider_cache_requires_current_adapter_and_prompt_contract(tmp_path) -> None:
    provider = SimpleNamespace(
        provider_id="openai",
        adapter="openai_responses",
        resolved_model=lambda: "gpt-test",
        resolved_base_url=lambda: "https://example.test/v1",
    )
    runner = object.__new__(MultiLlmArc3Runner)
    runner._llm_router = SimpleNamespace(
        prompt_section_names=lambda _provider: ("base", "vision")
    )
    node = SimpleNamespace(path=tmp_path)
    provenance = {
        "cache_contract_version": 1,
        "provider_id": "openai",
        "adapter": "openai_responses",
        "model": "gpt-test",
        "base_url": "https://example.test/v1",
        "prompt_sections": ["base", "vision"],
    }
    (tmp_path / "llm_provider.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )
    assert runner._cached_provider_matches(node, provider)

    provenance["prompt_sections"] = ["base", "changed"]
    (tmp_path / "llm_provider.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )
    assert not runner._cached_provider_matches(node, provider)

    provenance["prompt_sections"] = ["base", "vision"]
    provenance["adapter"] = "anthropic_messages"
    (tmp_path / "llm_provider.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )
    assert not runner._cached_provider_matches(node, provider)
