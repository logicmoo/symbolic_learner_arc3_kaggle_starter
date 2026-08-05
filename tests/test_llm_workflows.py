from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from llm_providers import DEFAULT_CONFIG_PATH
from llm_workflows import (
    DEFAULT_WORKFLOW_PATH,
    LlmWorkflowEngine,
    WorkflowAwareLlmProviderRouter,
    WorkflowStep,
)


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class FakeUrlOpen:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request.full_url, timeout))
        return FakeResponse(self.payload)


def test_workflow_catalog_contains_current_verified_free_models(monkeypatch):
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = WorkflowAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    expected = {
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "openai/gpt-oss-20b:free",
        "cohere/north-mini-code:free",
        "poolside/laguna-xs-2.1:free",
        "inclusionai/ling-3.0-flash:free",
    }
    actual = {
        router.model_by_id[model_id].model
        for model_id in router.extension_model_ids
    }

    assert DEFAULT_WORKFLOW_PATH.exists()
    assert expected.issubset(actual)
    assert router.model_by_id["openrouter-gemma-4-26b-a4b"].vision is True
    assert router.model_by_id["openrouter-nemotron-3-ultra"].vision is False


def test_transactions_and_workflows_reference_valid_catalog_entries(monkeypatch):
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    router = WorkflowAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)

    assert {
        "full_artifact_bundle",
        "extract_scene_objects",
        "explain_object_changes",
        "induce_rules_from_prolog",
        "audit_artifact_bundle",
        "prolog_render_symbolic_evidence",
    }.issubset(router.transaction_by_id)
    assert {
        "level4_then_prolog_review",
        "staged_symbolic_analysis",
        "free_staged_symbolic_analysis",
    }.issubset(router.workflow_by_id)

    for workflow in router.workflows:
        for step in workflow.steps:
            assert step.transaction_id in router.transaction_by_id
            if step.profile_id:
                assert step.profile_id in router.profile_by_id


def test_live_openrouter_availability_checks_slug_and_free_pricing(monkeypatch):
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "1")
    model_slug = "google/gemma-4-26b-a4b-it:free"
    http = FakeUrlOpen(
        {
            "data": [
                {
                    "id": model_slug,
                    "pricing": {"prompt": "0", "completion": "0"},
                    "architecture": {
                        "input_modalities": ["text", "image"],
                        "output_modalities": ["text"],
                    },
                }
            ]
        }
    )
    router = WorkflowAwareLlmProviderRouter(
        DEFAULT_CONFIG_PATH,
        urlopen=http,
    )

    assert router.model_availability(
        "openrouter-gemma-4-26b-a4b", refresh=True
    ) == (True, "available and free")
    assert http.calls[0][0].endswith("/models")


def test_text_only_profile_cannot_run_vision_transaction(monkeypatch):
    monkeypatch.delenv("ARC3_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "0")
    router = WorkflowAwareLlmProviderRouter(DEFAULT_CONFIG_PATH)
    runner = SimpleNamespace(llm_router=lambda: router)
    engine = LlmWorkflowEngine(runner)
    transaction = router.transaction_by_id["extract_scene_objects"]
    step = WorkflowStep(
        step_id="bad",
        transaction_id=transaction.transaction_id,
        profile_id="openrouter-nemotron-3-ultra-rules",
        model_id=None,
        analysis_level=None,
        combine_group=None,
        continue_on_error=False,
    )

    with pytest.raises(RuntimeError, match="needs vision"):
        engine._resolve_profile(step, transaction)


def test_workflow_repeat_restarts_at_named_step_while_slot_is_true(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "0")
    path = tmp_path / "repeat_workflow.json"
    path.write_text(
        json.dumps(
            {
                "llm_transactions": [
                    {"id": "mark", "kind": "runner_method", "runner_method": "mark"},
                    {"id": "decide", "kind": "runner_method", "runner_method": "decide"},
                ],
                "llm_workflows": [
                    {
                        "id": "repeat_twice",
                        "repeat": {
                            "from": "mark",
                            "while_slot": "again",
                            "max_iterations": 3,
                        },
                        "steps": [
                            {"id": "mark", "transaction": "mark"},
                            {"id": "decide", "transaction": "decide"},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    router = WorkflowAwareLlmProviderRouter(DEFAULT_CONFIG_PATH, workflow_path=path)

    class Runner:
        def __init__(self):
            self.marks = 0
            self.engine = None

        def llm_router(self):
            return router

        def mark(self):
            self.marks += 1

        def decide(self):
            self.engine._workflow_slots = {
                "again": SimpleNamespace(value=self.marks < 2)
            }

    runner = Runner()
    engine = LlmWorkflowEngine(runner)
    runner.engine = engine
    engine.run("repeat_twice")
    assert runner.marks == 2
