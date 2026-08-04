from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]


def test_env_example_parses_and_covers_runtime_configuration() -> None:
    values = dotenv_values(ROOT / ".env.example")
    required = {
        "ARC3_LLM_PROVIDER",
        "ARC3_CONFIG_ROOT",
        "ARC3_LLM_CONFIG",
        "ARC3_LLM_SAVE_TRANSCRIPT",
        "ARC3_LLM_RESPONSE_DIR",
        "ARC3_LLM_JSON_RETRY",
        "OPENAI_API_KEY",
        "ARC3_OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "ARC3_CLAUDE_MODEL",
        "ARC3_CLAUDE_BASE_URL",
        "ARC3_UNSLOTH_API_KEY",
        "ARC3_UNSLOTH_MODEL",
        "ARC3_UNSLOTH_BASE_URL",
        "ARC3_UNSLOTH_HEALTH_URL",
        "ARC3_UNSLOTH_STATUS_URL",
        "ARC3_UNSLOTH_LOAD_URL",
        "ARC3_UNSLOTH_AUTO_LOAD",
        "ARC3_UNSLOTH_GGUF_VARIANT",
        "ARC3_UNSLOTH_MAX_SEQ_LENGTH",
        "ARC3_UNSLOTH_N_PARALLEL",
        "ARC3_UNSLOTH_GPU_MEMORY_MODE",
        "ARC3_UNSLOTH_LOAD_TIMEOUT",
        "ARC3_UNSLOTH_FORCE_CANCEL_ACTIVE",
        "ARC3_UNSLOTH_TRUST_REMOTE_CODE",
        "HF_TOKEN",
        "ARC3_RUNTIME_HOME",
        "ARC3_TREE_ROOT",
        "ARC3_WEB_HOST",
        "ARC3_WEB_PORT",
        "ARC3_WEB_TOKEN",
        "ARC3_PYCHARM_DEBUG",
        "ARC3_PYCHARM_HOST",
        "ARC3_PYCHARM_PORT",
        "KAGGLE_API_TOKEN",
    }

    assert required.issubset(values)
    assert values["ARC3_UNSLOTH_API_KEY"].startswith("sk-unsloth-")
    assert "EXAMPLE" in values["ARC3_UNSLOTH_API_KEY"]
    assert values["ARC3_UNSLOTH_AUTO_LOAD"] == "1"
    assert values["ARC3_UNSLOTH_GGUF_VARIANT"] == "UD-Q4_K_XL"
    assert values["ARC3_UNSLOTH_MAX_SEQ_LENGTH"] == "131072"
    assert values["ARC3_LLM_SAVE_TRANSCRIPT"] == "1"
    assert values["ARC3_LLM_JSON_RETRY"] == "1"
    assert values["ARC3_CONFIG_ROOT"].endswith("/config")
    assert values["ARC3_LLM_CONFIG"].endswith("/config/llm_providers.json")
    assert "ARC3_PROMPTS_ROOT" not in values
    assert "ARC3_ENVIRONMENT_FILES" not in values
    assert values["ARC3_WEB_HOST"] == "127.0.0.1"
