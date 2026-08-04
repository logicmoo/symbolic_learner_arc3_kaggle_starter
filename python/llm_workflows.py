from __future__ import annotations

import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from gpt_bridge import (
    ARTIFACT_KEYS,
    PAIR_ONLY,
    _json_payload,
    _plain_prolog,
    _read,
)
from llm_model_catalog import (
    CatalogAwareLlmProviderRouter,
    ModelDefinition,
    ProfileDefinition,
)
from llm_providers import LlmConfigurationError, ProviderSpec
from llm_transcripts import finalize_last_transcript
from project_paths import prompts_path

DEFAULT_WORKFLOW_PATH = Path(__file__).resolve().parents[1] / "config" / "llm_workflows.json"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "y"}


def _data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


@dataclass(frozen=True)
class TransactionDefinition:
    transaction_id: str
    label: str
    kind: str
    requires_vision: bool
    include_parent_image: bool
    include_current_image: bool
    output_keys: tuple[str, ...]
    input_files: tuple[str, ...]
    instructions: str
    output_file: str | None
    runner_method: str | None
    combine_safe: bool

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TransactionDefinition":
        transaction_id = _text(raw.get("id"))
        if not transaction_id:
            raise LlmConfigurationError("Every llm_transactions entry requires id")
        kind = _text(raw.get("kind"))
        if kind not in {"full_analysis", "llm_artifacts", "llm_text", "runner_method"}:
            raise LlmConfigurationError(
                f"Transaction {transaction_id!r} has unsupported kind {kind!r}"
            )
        output_keys = tuple(_text(item) for item in raw.get("output_keys") or ())
        unknown = [key for key in output_keys if key not in ARTIFACT_KEYS]
        if unknown:
            raise LlmConfigurationError(
                f"Transaction {transaction_id!r} has unknown artifact keys: "
                + ", ".join(unknown)
            )
        output_file = _text(raw.get("output_file")) or None
        runner_method = _text(raw.get("runner_method")) or None
        if kind == "llm_artifacts" and not output_keys:
            raise LlmConfigurationError(
                f"Transaction {transaction_id!r} needs output_keys"
            )
        if kind == "llm_text" and not output_file:
            raise LlmConfigurationError(
                f"Transaction {transaction_id!r} needs output_file"
            )
        if kind == "runner_method" and not runner_method:
            raise LlmConfigurationError(
                f"Transaction {transaction_id!r} needs runner_method"
            )
        return cls(
            transaction_id=transaction_id,
            label=_text(raw.get("label")) or transaction_id,
            kind=kind,
            requires_vision=bool(raw.get("requires_vision", False)),
            include_parent_image=bool(raw.get("include_parent_image", False)),
            include_current_image=bool(raw.get("include_current_image", False)),
            output_keys=output_keys,
            input_files=tuple(_text(item) for item in raw.get("input_files") or ()),
            instructions=_text(raw.get("instructions")),
            output_file=output_file,
            runner_method=runner_method,
            combine_safe=bool(raw.get("combine_safe", False)),
        )


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    transaction_id: str
    profile_id: str | None
    model_id: str | None
    analysis_level: int | None
    combine_group: str | None
    continue_on_error: bool

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "WorkflowStep":
        step_id = _text(raw.get("id"))
        transaction_id = _text(raw.get("transaction"))
        if not step_id or not transaction_id:
            raise LlmConfigurationError("Every workflow step requires id and transaction")
        level_value = raw.get("analysis_level")
        level = None if level_value is None else int(level_value)
        if level is not None and level not in {2, 3, 4}:
            raise LlmConfigurationError(
                f"Workflow step {step_id!r} analysis_level must be 2, 3, or 4"
            )
        return cls(
            step_id=step_id,
            transaction_id=transaction_id,
            profile_id=_text(raw.get("profile")) or None,
            model_id=_text(raw.get("model")) or None,
            analysis_level=level,
            combine_group=_text(raw.get("combine_group")) or None,
            continue_on_error=bool(raw.get("continue_on_error", False)),
        )


@dataclass(frozen=True)
class WorkflowDefinition:
    workflow_id: str
    label: str
    description: str
    steps: tuple[WorkflowStep, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "WorkflowDefinition":
        workflow_id = _text(raw.get("id"))
        if not workflow_id:
            raise LlmConfigurationError("Every llm_workflows entry requires id")
        raw_steps = raw.get("steps")
        if not isinstance(raw_steps, list) or not raw_steps:
            raise LlmConfigurationError(
                f"Workflow {workflow_id!r} requires a nonempty steps list"
            )
        return cls(
            workflow_id=workflow_id,
            label=_text(raw.get("label")) or workflow_id,
            description=_text(raw.get("description")),
            steps=tuple(
                WorkflowStep.from_mapping(item)
                for item in raw_steps
                if isinstance(item, Mapping)
            ),
        )


class WorkflowAwareLlmProviderRouter(CatalogAwareLlmProviderRouter):
    """Catalog router extended with optional transactions and workflows.

    The normal lowercase-g / level-4 path remains unchanged. The companion
    workflow file contributes additional models and profiles plus specialized
    transactions that can be orchestrated only when requested.
    """

    def __init__(
        self,
        config_path: str | Path,
        *,
        workflow_path: str | Path | None = None,
        urlopen: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self.base_catalog_path = Path(config_path).expanduser().resolve()
        self.workflow_path = Path(
            workflow_path
            or os.environ.get("ARC3_LLM_WORKFLOW_CONFIG")
            or DEFAULT_WORKFLOW_PATH
        ).expanduser().resolve()
        base = json.loads(self.base_catalog_path.read_text(encoding="utf-8"))
        extension = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        if not isinstance(base, dict) or not isinstance(extension, dict):
            raise LlmConfigurationError("LLM catalogs must be JSON objects")

        merged = dict(base)
        merged_prompts = dict(base.get("prompt_text") or {})
        for key, value in (extension.get("prompt_text") or {}).items():
            if key in merged_prompts and merged_prompts[key] != value:
                raise LlmConfigurationError(
                    f"Workflow prompt section {key!r} conflicts with the base catalog"
                )
            merged_prompts[key] = value
        merged["prompt_text"] = merged_prompts
        merged["llm_models"] = [
            *(base.get("llm_models") or []),
            *(extension.get("llm_models") or []),
        ]
        merged["llm_profiles"] = [
            *(base.get("llm_profiles") or []),
            *(extension.get("llm_profiles") or []),
        ]

        import tempfile

        handle, temporary_name = tempfile.mkstemp(
            prefix="arc3_workflow_catalog_", suffix=".json"
        )
        os.close(handle)
        self._workflow_merged_path = Path(temporary_name)
        self._workflow_merged_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self._workflow_urlopen = urlopen or urllib.request.urlopen
        self._openrouter_cache: tuple[float, dict[str, dict[str, Any]]] | None = None
        super().__init__(self._workflow_merged_path, urlopen=urlopen, **kwargs)
        self.catalog_path = self.base_catalog_path

        self.extension_model_ids = {
            _text(item.get("id"))
            for item in extension.get("llm_models") or []
            if isinstance(item, Mapping)
        }
        self.profile_transactions = {
            _text(item.get("id")): _text(item.get("transaction"))
            or "full_artifact_bundle"
            for item in extension.get("llm_profiles") or []
            if isinstance(item, Mapping)
        }
        for profile in self.profiles:
            self.profile_transactions.setdefault(
                profile.profile_id, "full_artifact_bundle"
            )

        self.transactions = tuple(
            TransactionDefinition.from_mapping(item)
            for item in extension.get("llm_transactions") or []
            if isinstance(item, Mapping)
        )
        self.transaction_by_id = {
            item.transaction_id: item for item in self.transactions
        }
        if len(self.transaction_by_id) != len(self.transactions):
            raise LlmConfigurationError("Duplicate transaction ids are not allowed")

        self.workflows = tuple(
            WorkflowDefinition.from_mapping(item)
            for item in extension.get("llm_workflows") or []
            if isinstance(item, Mapping)
        )
        self.workflow_by_id = {item.workflow_id: item for item in self.workflows}
        if len(self.workflow_by_id) != len(self.workflows):
            raise LlmConfigurationError("Duplicate workflow ids are not allowed")
        for workflow in self.workflows:
            for step in workflow.steps:
                if step.transaction_id not in self.transaction_by_id:
                    raise LlmConfigurationError(
                        f"Workflow {workflow.workflow_id!r} references unknown "
                        f"transaction {step.transaction_id!r}"
                    )
                if step.profile_id and step.profile_id not in self.profile_by_id:
                    raise LlmConfigurationError(
                        f"Workflow {workflow.workflow_id!r} references unknown "
                        f"profile {step.profile_id!r}"
                    )
                if (
                    step.model_id
                    and step.model_id != "$selected"
                    and step.model_id not in self.model_by_id
                ):
                    raise LlmConfigurationError(
                        f"Workflow {workflow.workflow_id!r} references unknown "
                        f"model {step.model_id!r}"
                    )

    def __del__(self) -> None:
        try:
            super().__del__()
        finally:
            try:
                self._workflow_merged_path.unlink(missing_ok=True)
            except Exception:
                pass

    def transaction_for_profile(self, profile_id: str) -> TransactionDefinition:
        transaction_id = self.profile_transactions.get(
            profile_id, "full_artifact_bundle"
        )
        return self.transaction_by_id[transaction_id]

    def _openrouter_models(self, *, refresh: bool = False) -> dict[str, dict[str, Any]]:
        now = time.monotonic()
        ttl = float(os.environ.get("ARC3_OPENROUTER_MODEL_TTL", "600"))
        if (
            not refresh
            and self._openrouter_cache is not None
            and now - self._openrouter_cache[0] <= ttl
        ):
            return self._openrouter_cache[1]
        backend = self.backend_by_id.get("openrouter")
        if backend is None:
            return {}
        base_url = (
            os.environ.get(backend.base_url_env, "").strip()
            if backend.base_url_env
            else ""
        ) or backend.base_url or "https://openrouter.ai/api/v1"
        endpoint = base_url.rstrip("/") + "/models"
        headers = {"Accept": "application/json"}
        key = os.environ.get(backend.api_key_env or "", "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        request = urllib.request.Request(endpoint, headers=headers)
        timeout = float(os.environ.get("ARC3_OPENROUTER_MODEL_TIMEOUT", "3"))
        with self._workflow_urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        rows = payload.get("data") if isinstance(payload, Mapping) else None
        result = {
            _text(item.get("id")): dict(item)
            for item in rows or []
            if isinstance(item, Mapping) and _text(item.get("id"))
        }
        self._openrouter_cache = (now, result)
        return result

    @staticmethod
    def _zero_price(item: Mapping[str, Any]) -> bool:
        pricing = item.get("pricing")
        if not isinstance(pricing, Mapping):
            return item.get("is_free") is True or _text(item.get("id")).endswith(":free")
        values = [pricing.get("prompt"), pricing.get("completion")]
        try:
            return all(float(value or 0) == 0 for value in values)
        except (TypeError, ValueError):
            return _text(item.get("id")).endswith(":free")

    def model_availability(
        self, model_id: str, *, refresh: bool = False
    ) -> tuple[bool, str]:
        model = self.model_by_id[model_id]
        if model.provider_id != "openrouter":
            return True, "not an OpenRouter model"
        if not _bool_env("ARC3_OPENROUTER_VERIFY_MODELS", True):
            return True, "live verification disabled"
        try:
            item = self._openrouter_models(refresh=refresh).get(model.resolved_model())
        except Exception as exc:
            if model_id in self.extension_model_ids:
                return True, f"static verification fallback: {exc}"
            return True, f"availability not checked: {exc}"
        if item is None:
            return False, "not returned by OpenRouter /models"
        if not self._zero_price(item):
            return False, "model is currently not free"
        return True, "available and free"

    def configured_model_ids(self) -> tuple[str, ...]:
        candidates = super().configured_model_ids()
        result: list[str] = []
        for model_id in candidates:
            available, _state = self.model_availability(model_id)
            if available:
                result.append(model_id)
        return tuple(result)


class LlmWorkflowEngine:
    def __init__(self, runner: Any) -> None:
        self.runner = runner
        router = runner.llm_router()
        if not isinstance(router, WorkflowAwareLlmProviderRouter):
            raise RuntimeError("The ARC3 workflow router is not installed")
        self.router = router

    def _resolve_profile(
        self, step: WorkflowStep, transaction: TransactionDefinition
    ) -> ProfileDefinition | None:
        if transaction.kind == "runner_method":
            return None
        if step.profile_id:
            profile = self.router.profile_by_id[step.profile_id]
        else:
            model_id = step.model_id
            if not model_id or model_id == "$selected":
                model_id = self.router.active_model().model_id
            level = step.analysis_level or self.router.model_by_id[model_id].default_level
            candidates = [
                item
                for item in self.router.profiles_for_model(model_id)
                if item.analysis_level == level
            ]
            if not candidates:
                raise RuntimeError(
                    f"Model {model_id!r} has no level {level} profile"
                )
            profile = next(
                (
                    item
                    for item in candidates
                    if self.router.profile_transactions.get(item.profile_id)
                    == transaction.transaction_id
                ),
                candidates[0],
            )
        model = self.router.model_by_id[profile.model_id]
        if transaction.requires_vision and not model.vision:
            raise RuntimeError(
                f"Transaction {transaction.transaction_id!r} needs vision, but "
                f"model {model.model_id!r} is text-only"
            )
        available, state = self.router.model_availability(model.model_id)
        if not available:
            raise RuntimeError(f"Model {model.model_id!r} unavailable: {state}")
        return profile

    def _transaction_context(
        self, transaction: TransactionDefinition, store: Any, node: Any
    ) -> str:
        parent = store.parent_node(node)
        parts: list[str] = []
        metadata = store.metadata(node)
        parts.append(
            "STATE METADATA:\n"
            + json.dumps(metadata, ensure_ascii=False, indent=2, default=str)
        )
        for filename in transaction.input_files:
            if filename == "object_registry.pl":
                path = store.object_registry_path
                if path.exists():
                    parts.append(f"LEVEL {filename}:\n" + _read(path))
                continue
            current = node.path / filename
            if current.exists():
                parts.append(f"CURRENT {filename}:\n" + _read(current))
            if parent is not None:
                previous = parent.path / filename
                if previous.exists():
                    parts.append(f"PARENT {filename}:\n" + _read(previous))
        return "\n\n".join(parts)

    def _request_content(
        self,
        transaction: TransactionDefinition,
        profile: ProfileDefinition,
        store: Any,
        node: Any,
        *,
        output_keys: Iterable[str] | None = None,
        combined_instructions: str | None = None,
    ) -> list[dict[str, Any]]:
        prompt = self.router.compose_prompt()
        keys = tuple(output_keys or transaction.output_keys)
        if transaction.kind == "llm_text":
            contract = (
                "Return exactly one strict JSON object with one key named "
                "audit_md whose value is a Markdown string."
            )
        else:
            contract = (
                "Return exactly one strict JSON object containing new_identities "
                "plus only these artifact keys: "
                + ", ".join(keys)
                + ". Omit every other artifact key."
            )
        instruction = combined_instructions or transaction.instructions
        text = (
            prompt
            + "\n\n"
            + contract
            + ("\n\n" + instruction if instruction else "")
            + "\n\nTRANSACTION INPUTS:\n"
            + self._transaction_context(transaction, store, node)
        )
        content: list[dict[str, Any]] = [
            {"type": "input_text", "text": text}
        ]
        parent = store.parent_node(node)
        if transaction.include_parent_image and parent is not None:
            content.extend(
                [
                    {"type": "input_text", "text": "Previous ARC3 state image:"},
                    {
                        "type": "input_image",
                        "image_url": _data_url(parent.image_path),
                        "detail": profile.parent_image_detail,
                    },
                ]
            )
        if transaction.include_current_image:
            content.extend(
                [
                    {"type": "input_text", "text": "Current ARC3 state image:"},
                    {
                        "type": "input_image",
                        "image_url": _data_url(node.image_path),
                        "detail": profile.current_image_detail,
                    },
                ]
            )
        return content

    def _write_artifacts(
        self,
        store: Any,
        node: Any,
        bundle: Mapping[str, Any],
        output_keys: Iterable[str],
    ) -> None:
        analyzer = self.runner._analyzer()
        if bundle.get("new_identities") or "objects_pl" in output_keys:
            analyzer._merge_new_identities(store, dict(bundle))
        parent = store.parent_node(node)
        for key in output_keys:
            filename = ARTIFACT_KEYS[key]
            text = _plain_prolog(bundle.get(key, ""))
            if filename == "objects.pl":
                text = analyzer._normalize_objects(store, node, text)
            if parent is None and filename in PAIR_ONLY and not text:
                continue
            destination = node.path / filename
            destination.write_text(
                text + ("" if text.endswith("\n") else "\n"),
                encoding="utf-8",
            )
        store.refresh_readme(node)
        if parent is not None:
            store.refresh_readme(parent)

    def _provider_call(
        self,
        transaction: TransactionDefinition,
        profile: ProfileDefinition,
        *,
        output_keys: Iterable[str] | None = None,
        combined_instructions: str | None = None,
    ) -> Any:
        store, node = self.runner._require_node()
        self.router.select_profile(profile.profile_id)
        self.runner._active_llm_analysis_level = profile.analysis_level
        try:
            with self.router.profile_environment(profile):
                content = self._request_content(
                    transaction,
                    profile,
                    store,
                    node,
                    output_keys=output_keys,
                    combined_instructions=combined_instructions,
                )
                response = self.router.responses.create(
                    model="profile-selected",
                    input=[{"role": "user", "content": content}],
                    reasoning={"effort": profile.reasoning_effort},
                    max_output_tokens=profile.max_output_tokens,
                )
            return response
        except Exception as exc:
            finalize_last_transcript(store, node, error=str(exc))
            marker = getattr(self.runner, "_mark_llm_provider_failed", None)
            if callable(marker):
                marker(self.router.current_spec(), exc)
            raise
        finally:
            self.runner._active_llm_analysis_level = None

    def _finish_call(self, profile: ProfileDefinition) -> Path | None:
        store, node = self.runner._require_node()
        marker = getattr(self.runner, "_mark_llm_provider_succeeded", None)
        if callable(marker):
            marker(self.router.current_spec())
        self.runner._write_provider_provenance(
            node,
            self.router.current_spec(),
            analysis_level=profile.analysis_level,
        )
        return finalize_last_transcript(store, node)

    def _run_artifact_transaction(
        self,
        transaction: TransactionDefinition,
        profile: ProfileDefinition,
        *,
        output_keys: Iterable[str] | None = None,
        combined_instructions: str | None = None,
    ) -> None:
        keys = tuple(output_keys or transaction.output_keys)
        response = self._provider_call(
            transaction,
            profile,
            output_keys=keys,
            combined_instructions=combined_instructions,
        )
        bundle = _json_payload(str(response.output_text))
        store, node = self.runner._require_node()
        self._write_artifacts(store, node, bundle, keys)
        transcript = self._finish_call(profile)
        print(
            f"Transaction {transaction.label} complete with {profile.label}."
        )
        if transcript is not None:
            print(f"LLM comparison transcript: {transcript}")

    def _run_text_transaction(
        self, transaction: TransactionDefinition, profile: ProfileDefinition
    ) -> None:
        response = self._provider_call(transaction, profile)
        payload = json.loads(str(response.output_text))
        text = _text(payload.get("audit_md"))
        if not text:
            raise RuntimeError(
                f"Transaction {transaction.transaction_id!r} returned no audit_md"
            )
        _store, node = self.runner._require_node()
        destination = node.path / str(transaction.output_file)
        destination.write_text(text.rstrip() + "\n", encoding="utf-8")
        transcript = self._finish_call(profile)
        print(f"{transaction.label}: {destination}")
        if transcript is not None:
            print(f"LLM comparison transcript: {transcript}")

    def _run_full_analysis(
        self,
        transaction: TransactionDefinition,
        profile: ProfileDefinition,
    ) -> None:
        self.runner._run_gpt_analysis_level(
            profile.analysis_level,
            profile_id=profile.profile_id,
            mode="workflow",
        )

    def _run_runner_method(self, transaction: TransactionDefinition) -> None:
        method = getattr(self.runner, str(transaction.runner_method), None)
        if not callable(method):
            raise RuntimeError(
                f"Runner has no callable {transaction.runner_method!r}"
            )
        method()

    def _combined_steps(
        self, workflow: WorkflowDefinition
    ) -> list[tuple[list[WorkflowStep], TransactionDefinition, ProfileDefinition | None]]:
        result: list[
            tuple[list[WorkflowStep], TransactionDefinition, ProfileDefinition | None]
        ] = []
        index = 0
        while index < len(workflow.steps):
            step = workflow.steps[index]
            transaction = self.router.transaction_by_id[step.transaction_id]
            profile = self._resolve_profile(step, transaction)
            group = [step]
            if (
                step.combine_group
                and transaction.kind == "llm_artifacts"
                and transaction.combine_safe
                and profile is not None
            ):
                next_index = index + 1
                while next_index < len(workflow.steps):
                    candidate = workflow.steps[next_index]
                    if candidate.combine_group != step.combine_group:
                        break
                    candidate_transaction = self.router.transaction_by_id[
                        candidate.transaction_id
                    ]
                    candidate_profile = self._resolve_profile(
                        candidate, candidate_transaction
                    )
                    if (
                        candidate_transaction.kind != "llm_artifacts"
                        or not candidate_transaction.combine_safe
                        or candidate_profile is None
                        or candidate_profile.profile_id != profile.profile_id
                    ):
                        break
                    group.append(candidate)
                    next_index += 1
                index = next_index
            else:
                index += 1
            result.append((group, transaction, profile))
        return result

    def run(self, workflow_id: str) -> None:
        workflow = self.router.workflow_by_id[workflow_id]
        selected_model = self.router.active_model().model_id
        print(f"\nWORKFLOW: {workflow.label}")
        if workflow.description:
            print(workflow.description)
        for group, transaction, profile in self._combined_steps(workflow):
            step_names = ", ".join(step.step_id for step in group)
            print(f"\nWorkflow step(s): {step_names}")
            try:
                if len(group) > 1:
                    transactions = [
                        self.router.transaction_by_id[step.transaction_id]
                        for step in group
                    ]
                    output_keys: list[str] = []
                    for item in transactions:
                        for key in item.output_keys:
                            if key not in output_keys:
                                output_keys.append(key)
                    instructions = "\n\n".join(
                        item.instructions for item in transactions if item.instructions
                    )
                    merged = replace(
                        transaction,
                        label=" + ".join(item.label for item in transactions),
                        include_parent_image=any(
                            item.include_parent_image for item in transactions
                        ),
                        include_current_image=any(
                            item.include_current_image for item in transactions
                        ),
                        input_files=tuple(
                            dict.fromkeys(
                                filename
                                for item in transactions
                                for filename in item.input_files
                            )
                        ),
                    )
                    assert profile is not None
                    self._run_artifact_transaction(
                        merged,
                        profile,
                        output_keys=output_keys,
                        combined_instructions=instructions,
                    )
                    continue

                step = group[0]
                transaction = self.router.transaction_by_id[step.transaction_id]
                profile = self._resolve_profile(step, transaction)
                if transaction.kind == "runner_method":
                    self._run_runner_method(transaction)
                elif transaction.kind == "full_analysis":
                    assert profile is not None
                    self._run_full_analysis(transaction, profile)
                elif transaction.kind == "llm_artifacts":
                    assert profile is not None
                    self._run_artifact_transaction(transaction, profile)
                elif transaction.kind == "llm_text":
                    assert profile is not None
                    self._run_text_transaction(transaction, profile)
            except Exception as exc:
                if all(step.continue_on_error for step in group):
                    print(f"Workflow step failed but is optional: {exc}")
                    continue
                raise RuntimeError(
                    f"Workflow {workflow.workflow_id!r} stopped at {step_names}: {exc}"
                ) from exc
        try:
            self.router.select_model(selected_model)
        except Exception:
            pass
        print(f"\nWorkflow {workflow.label} complete.")


def install_workflow_router() -> None:
    from multillm_runner import MultiLlmArc3Runner

    if getattr(MultiLlmArc3Runner, "_arc3_workflows_installed", False):
        return

    def llm_router(self: Any) -> WorkflowAwareLlmProviderRouter:
        if not isinstance(self._llm_router, WorkflowAwareLlmProviderRouter):
            self._llm_router = WorkflowAwareLlmProviderRouter(prompts_path())
        return self._llm_router

    def reload_llm_router(
        self: Any,
        *,
        active_model_id: str | None = None,
    ) -> WorkflowAwareLlmProviderRouter:
        old = self._llm_router
        if active_model_id is None and isinstance(
            old, WorkflowAwareLlmProviderRouter
        ):
            active_model_id = old.active_model().model_id
        self._llm_router = WorkflowAwareLlmProviderRouter(prompts_path())
        self._gpt_analyzer = None
        if active_model_id:
            try:
                self._llm_router.select_model(active_model_id)
            except Exception:
                pass
        return self._llm_router

    MultiLlmArc3Runner.llm_router = llm_router
    MultiLlmArc3Runner.reload_llm_router = reload_llm_router
    MultiLlmArc3Runner._arc3_workflows_installed = True


def _open_file(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        subprocess.run([editor, str(path)], check=False)
    else:
        print(path.read_text(encoding="utf-8"))
        print(f"Edit workflow catalog at: {path}")


def run_workflow_menu(runner: Any) -> None:
    router = runner.llm_router()
    if not isinstance(router, WorkflowAwareLlmProviderRouter):
        raise RuntimeError("Workflow router is not installed")
    while True:
        print("\nOPTIONAL LLM/PROLOG WORKFLOWS")
        for index, workflow in enumerate(router.workflows, start=1):
            print(f" {index:>2}. {workflow.label}")
            if workflow.description:
                print(f"      {workflow.description}")
        print(" [R] Refresh live OpenRouter model availability")
        print(" [E] Edit transactions, free models, and workflows")
        print(" [Enter] Cancel")
        choice = input("Workflow: ").strip()
        if not choice:
            return
        if choice.lower() in {"e", "edit"}:
            _open_file(router.workflow_path)
            runner.reload_llm_router()
            router = runner.llm_router()
            continue
        if choice.lower() in {"r", "refresh"}:
            print("\nOpenRouter availability:")
            for model_id in sorted(router.extension_model_ids):
                model = router.model_by_id[model_id]
                available, state = router.model_availability(
                    model_id, refresh=True
                )
                marker = "yes" if available else "no"
                print(
                    f"  [{marker}] {model.label}: {model.resolved_model()} — {state}"
                )
            continue
        index = int(choice) - 1
        if not 0 <= index < len(router.workflows):
            raise ValueError("Workflow number is out of range")
        LlmWorkflowEngine(runner).run(router.workflows[index].workflow_id)
        return


def install_workflow_ui(ui_module: Any) -> None:
    if getattr(ui_module.read_key, "_arc3_workflow_ui", False):
        return
    original_read_key = ui_module.read_key
    original_print_controls = ui_module.print_controls

    def read_key() -> str:
        key = original_read_key()
        if key != "W":
            return key
        from multillm_runner import last_runner

        runner = last_runner()
        if runner is None:
            print("No active ARC3 runner is available for workflow execution.")
        else:
            try:
                run_workflow_menu(runner)
            except Exception as exc:
                print(f"LLM workflow error: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        original_print_controls(runner, rows)
        print(
            "Optional orchestration: (W) run/edit LLM transactions and Prolog workflows"
        )

    read_key._arc3_workflow_ui = True  # type: ignore[attr-defined]
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
