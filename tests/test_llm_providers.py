from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from llm_providers import DEFAULT_CONFIG_PATH, LlmProviderRouter, _anthropic_blocks


class FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text='{"ok":true}')


class FakeOpenAI:
    def __init__(self, **kwargs) -> None:
        self.init = kwargs
        self.responses = FakeResponses()


def write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "default_provider": "cloud",
                "providers": [
                    {
                        "id": "cloud",
                        "label": "Cloud",
                        "adapter": "openai_responses",
                        "model": "cloud-model",
                        "api_key_env": "TEST_CLOUD_KEY",
                        "enabled": "auto",
                        "supports_reasoning": True,
                    },
                    {
                        "id": "local",
                        "label": "Local",
                        "adapter": "openai_responses",
                        "model": "local-model",
                        "base_url": "http://localhost:8888/v1",
                        "api_key_optional": True,
                        "enabled": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def test_cycle_skips_missing_key(tmp_path, monkeypatch):
    config = tmp_path / "providers.json"
    write_config(config)
    monkeypatch.delenv("TEST_CLOUD_KEY", raising=False)
    router = LlmProviderRouter(config, openai_client_factory=FakeOpenAI)

    assert router.cycle().provider_id == "local"
    assert router.cycle().provider_id == "local"


def test_openai_route_uses_selected_model(tmp_path, monkeypatch):
    config = tmp_path / "providers.json"
    write_config(config)
    monkeypatch.setenv("TEST_CLOUD_KEY", "secret")
    clients = []

    def factory(**kwargs):
        client = FakeOpenAI(**kwargs)
        clients.append(client)
        return client

    router = LlmProviderRouter(config, openai_client_factory=factory)
    router.select("local")
    response = router.responses.create(
        model="ignored",
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "x"}],
            }
        ],
        reasoning={"effort": "high"},
        max_output_tokens=99,
    )

    assert response.output_text == '{"ok":true}'
    assert clients[0].responses.calls[0] == {
        "model": "local-model",
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "x"}],
            }
        ],
        "max_output_tokens": 99,
    }


def test_default_unsloth_requires_studio_api_key(monkeypatch):
    monkeypatch.delenv("ARC3_UNSLOTH_API_KEY", raising=False)
    router = LlmProviderRouter(DEFAULT_CONFIG_PATH, openai_client_factory=FakeOpenAI)
    unsloth = next(spec for spec in router.specs if spec.provider_id == "unsloth")

    assert unsloth.configuration_state() == (
        False,
        "missing ARC3_UNSLOTH_API_KEY",
    )
    assert "unsloth" not in {spec.provider_id for spec in router.configured_specs()}


def test_default_unsloth_accepts_studio_api_key(monkeypatch):
    monkeypatch.setenv("ARC3_UNSLOTH_API_KEY", "sk-unsloth-test-key")
    router = LlmProviderRouter(DEFAULT_CONFIG_PATH, openai_client_factory=FakeOpenAI)
    unsloth = next(spec for spec in router.specs if spec.provider_id == "unsloth")

    assert unsloth.configuration_state() == (True, "configured")
    assert "unsloth" in {spec.provider_id for spec in router.configured_specs()}


def test_anthropic_image_translation():
    encoded = "aGVsbG8="
    blocks = _anthropic_blocks(
        [
            {"type": "input_text", "text": "look"},
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{encoded}",
            },
        ]
    )

    assert blocks[0] == {"type": "text", "text": "look"}
    assert blocks[1]["source"]["media_type"] == "image/png"
    assert blocks[1]["source"]["data"] == encoded
