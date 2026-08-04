from __future__ import annotations

from llm_model_catalog import CatalogAwareLlmProviderRouter
from llm_providers import DEFAULT_CONFIG_PATH


def test_default_catalog_has_backends_models_and_profiles(monkeypatch) -> None:
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = CatalogAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    assert len(router.backends) == 5
    assert len(router.models) >= 7
    assert len(router.profiles) >= 21
    assert len(router.backend_by_id) == len(router.backends)
    assert len(router.model_by_id) == len(router.models)
    assert len(router.profile_by_id) == len(router.profiles)


def test_every_checked_in_model_has_light_deep_and_extreme_profiles(monkeypatch) -> None:
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = CatalogAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    for model in router.models:
        profiles = router.profiles_for_model(model.model_id)
        assert {profile.analysis_level for profile in profiles} == {2, 3, 4}
        assert all(profile.prompt_text for profile in profiles)
        assert all(profile.max_output_tokens > 0 for profile in profiles)
        assert all(profile.timeout_seconds > 0 for profile in profiles)


def test_openrouter_backend_exposes_multiple_selectable_models(monkeypatch) -> None:
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = CatalogAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    openrouter_models = {
        model.model
        for model in router.models
        if model.provider_id == "openrouter"
    }
    assert "openrouter/free" in openrouter_models
    assert "nvidia/nemotron-nano-12b-v2-vl:free" in openrouter_models
    assert (
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
        in openrouter_models
    )


def test_single_and_batch_selection_are_independent(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = CatalogAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    router.select_model("openai-gpt-5.6")
    light = router.activate_level(2, mode="single")
    assert light.provider_id == "openai-gpt-5.6-light"
    assert router.profile_for_spec(light).single_enabled is True

    batch_ids = {profile.profile_id for profile in router.batch_profiles()}
    assert "openai-gpt-5.6-light" not in batch_ids
    assert "openrouter-nemotron-omni-deep" in batch_ids
