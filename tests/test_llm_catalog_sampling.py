from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from llm_catalog_sampling import install_profile_sampling
from llm_providers import LlmProviderRouter


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text='{"ok":true}',
            id="response-test",
            model=kwargs.get("model"),
            status="completed",
            usage=None,
        )


class FakeOpenAI:
    def __init__(self, **kwargs) -> None:
        self.init = kwargs
        self.responses = FakeResponses()


def write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "default_provider": "local",
                "prompt_text": {"base": ["Return JSON"]},
                "llm_providers": [
                    {
                        "id": "local",
                        "adapter": "openai_responses",
                        "model": "local-model",
                        "base_url": "http://localhost:8888/v1",
                        "api_key_optional": True,
                        "enabled": True,
                        "prompt_text": ["base"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_openai_compatible_profile_parameters_are_forwarded(
    tmp_path, monkeypatch
) -> None:
    config = tmp_path / "providers.json"
    write_config(config)
    clients = []

    def factory(**kwargs):
        client = FakeOpenAI(**kwargs)
        clients.append(client)
        return client

    install_profile_sampling()
    monkeypatch.setenv("ARC3_LLM_TEMPERATURE", "0.15")
    monkeypatch.setenv("ARC3_LLM_TOP_P", "0.85")
    monkeypatch.setenv("ARC3_LLM_SEED", "17")
    monkeypatch.setenv("ARC3_LLM_TIMEOUT_SECONDS", "123")
    router = LlmProviderRouter(config, openai_client_factory=factory)

    router.responses.create(
        input=[{"role": "user", "content": "test"}],
        max_output_tokens=99,
    )

    assert clients[0].init["timeout"] == 123.0
    assert clients[0].responses.calls[0]["temperature"] == 0.15
    assert clients[0].responses.calls[0]["top_p"] == 0.85
    assert clients[0].responses.calls[0]["seed"] == 17
