from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from unsloth_studio import StudioAwareLlmProviderRouter


class FakeResponse:
    def __init__(self, value):
        self.value = value
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.value).encode("utf-8")


class FakeUrlOpen:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        if not self.values:
            raise AssertionError(f"Unexpected request: {request.full_url}")
        return FakeResponse(self.values.pop(0))


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text='{"ok":true}')


class FakeOpenAI:
    def __init__(self, **kwargs):
        self.init = kwargs
        self.responses = FakeResponses()


def write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "default_provider": "unsloth",
                "providers": [
                    {
                        "id": "unsloth",
                        "label": "Unsloth Studio local",
                        "adapter": "openai_responses",
                        "model": "unsloth/gemma-4-E2B-it-GGUF",
                        "api_key_env": "ARC3_UNSLOTH_API_KEY",
                        "base_url": "http://127.0.0.1:8888/v1",
                        "enabled": "auto",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def loaded_status():
    return {
        "active_model": "unsloth/gemma-4-E2B-it-GGUF",
        "model_identifier": "unsloth/gemma-4-E2B-it-GGUF",
        "gguf_variant": "UD-Q4_K_XL",
        "loading": [],
        "loaded": ["unsloth/gemma-4-E2B-it-GGUF"],
    }


def no_model_status():
    return {
        "active_model": None,
        "model_identifier": None,
        "gguf_variant": None,
        "loading": [],
        "loaded": [],
    }


def test_unloaded_studio_loads_model_before_response(tmp_path, monkeypatch):
    config = tmp_path / "providers.json"
    write_config(config)
    monkeypatch.setenv("ARC3_UNSLOTH_API_KEY", "sk-unsloth-test-key")
    monkeypatch.setenv("ARC3_UNSLOTH_GGUF_VARIANT", "UD-Q4_K_XL")
    http = FakeUrlOpen(
        [
            no_model_status(),
            {"status": "loaded", "model": "unsloth/gemma-4-E2B-it-GGUF"},
            loaded_status(),
        ]
    )
    clients = []

    def factory(**kwargs):
        client = FakeOpenAI(**kwargs)
        clients.append(client)
        return client

    router = StudioAwareLlmProviderRouter(
        config,
        urlopen=http,
        openai_client_factory=factory,
        sleep=lambda _seconds: None,
        clock=lambda: 0.0,
    )
    result = router.responses.create(
        model="ignored",
        input=[{"role": "user", "content": "test"}],
        max_output_tokens=10,
    )

    assert result.output_text == '{"ok":true}'
    assert [call[0].get_method() for call in http.calls] == ["GET", "POST", "GET"]
    assert http.calls[0][0].full_url.endswith("/api/inference/status")
    assert http.calls[1][0].full_url.endswith("/api/inference/load")
    payload = json.loads(http.calls[1][0].data)
    assert payload["model_path"] == "unsloth/gemma-4-E2B-it-GGUF"
    assert payload["gguf_variant"] == "UD-Q4_K_XL"
    assert payload["max_seq_length"] == 131072
    assert payload["n_parallel"] == 1
    assert payload["gpu_memory_mode"] == "auto"
    assert http.calls[1][0].headers["Authorization"] == "Bearer sk-unsloth-test-key"
    assert clients[0].responses.calls[0]["model"] == "unsloth/gemma-4-E2B-it-GGUF"


def test_loaded_studio_does_not_reload(tmp_path, monkeypatch):
    config = tmp_path / "providers.json"
    write_config(config)
    monkeypatch.setenv("ARC3_UNSLOTH_API_KEY", "sk-unsloth-test-key")
    http = FakeUrlOpen([loaded_status()])
    clients = []

    def factory(**kwargs):
        client = FakeOpenAI(**kwargs)
        clients.append(client)
        return client

    router = StudioAwareLlmProviderRouter(
        config,
        urlopen=http,
        openai_client_factory=factory,
    )
    router.responses.create(model="ignored", input=[], max_output_tokens=10)

    assert [call[0].get_method() for call in http.calls] == ["GET"]
    assert len(clients[0].responses.calls) == 1


def test_provider_status_distinguishes_server_from_loaded_model(tmp_path, monkeypatch):
    config = tmp_path / "providers.json"
    write_config(config)
    monkeypatch.setenv("ARC3_UNSLOTH_API_KEY", "sk-unsloth-test-key")
    router = StudioAwareLlmProviderRouter(
        config,
        urlopen=FakeUrlOpen([no_model_status()]),
        openai_client_factory=FakeOpenAI,
    )

    status = router.statuses(probe=True)[0]

    assert status.configured
    assert "no model loaded" in status.state
    assert "auto-load" in status.state
