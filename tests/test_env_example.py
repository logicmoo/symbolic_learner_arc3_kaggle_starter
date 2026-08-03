from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]


def test_env_example_parses_and_covers_runtime_configuration() -> None:
    values = dotenv_values(ROOT / ".env.example")
    required = {
        "ARC3_LLM_PROVIDER",
        "ARC3_LLM_CONFIG",
        "OPENAI_API_KEY",
        "ARC3_OPENAI_MODEL",
        "ANTHROPIC_API_KEY",
        "ARC3_CLAUDE_MODEL",
        "ARC3_CLAUDE_BASE_URL",
        "ARC3_UNSLOTH_API_KEY",
        "ARC3_UNSLOTH_MODEL",
        "ARC3_UNSLOTH_BASE_URL",
        "ARC3_UNSLOTH_HEALTH_URL",
        "ARC3_RUNTIME_HOME",
        "ARC3_PROMPTS_ROOT",
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
    assert values["ARC3_WEB_HOST"] == "127.0.0.1"
