from __future__ import annotations

import json

from llm_providers import DEFAULT_CONFIG_PATH


def test_catalog_json_references_are_complete() -> None:
    raw = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
    providers = {item["id"] for item in raw["llm_providers"]}
    models = {item["id"]: item for item in raw["llm_models"]}
    prompts = set(raw["prompt_text"])

    assert providers
    assert models
    assert raw["llm_profiles"]
    assert all(model["provider"] in providers for model in models.values())
    assert all(profile["model"] in models for profile in raw["llm_profiles"])
    assert all(
        set(profile["prompt_text"]).issubset(prompts)
        for profile in raw["llm_profiles"]
    )
    assert all(
        len(profile["prompt_text"]) == len(set(profile["prompt_text"]))
        for profile in raw["llm_profiles"]
    )
