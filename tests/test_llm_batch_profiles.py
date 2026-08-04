from __future__ import annotations

from pathlib import Path

from llm_batch_profiles import DEFAULT_BATCH_CONFIG, load_profiles


def test_default_batch_profiles_are_provider_specific() -> None:
    profiles = load_profiles(DEFAULT_BATCH_CONFIG)

    assert len(profiles) >= 6
    assert len({profile.profile_id for profile in profiles}) == len(profiles)
    assert all(profile.provider_id for profile in profiles)
    assert all(profile.model for profile in profiles)
    assert all(profile.analysis_level in {2, 3, 4} for profile in profiles)
    assert all(profile.max_output_tokens > 0 for profile in profiles)
    assert all(profile.timeout_seconds > 0 for profile in profiles)

    openrouter_models = {
        profile.model
        for profile in profiles
        if profile.provider_id == "openrouter-free"
    }
    assert "openrouter/free" in openrouter_models
    assert "nvidia/nemotron-nano-12b-v2-vl:free" in openrouter_models
    assert (
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
        in openrouter_models
    )


def test_same_model_can_have_different_parameters() -> None:
    profiles = load_profiles(DEFAULT_BATCH_CONFIG)
    omni = [
        profile
        for profile in profiles
        if profile.model
        == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    ]

    assert len(omni) >= 2
    assert len({profile.max_output_tokens for profile in omni}) >= 2
    assert len({profile.analysis_level for profile in omni}) >= 2
    assert len({profile.timeout_seconds for profile in omni}) >= 2


def test_batch_config_is_beside_unified_provider_config() -> None:
    assert DEFAULT_BATCH_CONFIG.name == "llm_batch_profiles.json"
    assert DEFAULT_BATCH_CONFIG.parent.name == "config"
    assert Path(DEFAULT_BATCH_CONFIG).exists()
