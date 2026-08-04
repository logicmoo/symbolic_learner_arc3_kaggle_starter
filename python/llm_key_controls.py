from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any

from project_paths import histories_root


def _runner() -> Any | None:
    from multillm_runner import last_runner

    return last_runner()


def run_checked_batch(runner: Any) -> None:
    """Run every profile currently marked batch_enabled in the catalog."""
    from llm_profile_editor import _run_batch

    _run_batch(runner)


def repeat_last_workflow(runner: Any) -> None:
    """Repeat the workflow most recently selected through uppercase W."""
    from llm_workflows import LlmWorkflowEngine, WorkflowAwareLlmProviderRouter

    router = runner.llm_router()
    if not isinstance(router, WorkflowAwareLlmProviderRouter):
        raise RuntimeError("Workflow router is not installed")
    workflow_id = getattr(runner, "_last_llm_workflow_id", None)
    if not workflow_id:
        print("No workflow has been selected yet. Press uppercase W first.")
        return
    workflow = router.workflow_by_id.get(str(workflow_id))
    if workflow is None:
        print(
            f"The last workflow {workflow_id!r} is no longer defined. "
            "Press uppercase W to select another workflow."
        )
        return
    print(f"Repeating workflow: {workflow.label}")
    LlmWorkflowEngine(runner).run(workflow.workflow_id)


def refresh_openrouter_models(runner: Any) -> None:
    """Refresh OpenRouter's live model list and show usable free catalog rows."""
    from llm_workflows import WorkflowAwareLlmProviderRouter

    router = runner.llm_router()
    if not isinstance(router, WorkflowAwareLlmProviderRouter):
        raise RuntimeError("Workflow router is not installed")

    models = [model for model in router.models if model.provider_id == "openrouter"]
    if not models:
        print("No OpenRouter models are configured.")
        return

    print("\nRefreshing OpenRouter free-model availability...")
    refresh_error: Exception | None = None
    try:
        router._openrouter_models(refresh=True)
    except Exception as exc:  # The per-model checker provides static fallback details.
        refresh_error = exc
        print(f"Live OpenRouter refresh failed: {exc}")

    specs = {spec.provider_id: spec for spec in router.specs}
    ready_count = 0
    for model in models:
        available, state = router.model_availability(model.model_id, refresh=False)
        profiles = router.profiles_for_model(model.model_id)
        configured = any(
            specs[profile.profile_id].configuration_state()[0]
            for profile in profiles
            if profile.profile_id in specs
        )
        usable = available and configured
        if usable:
            ready_count += 1
        marker = "ready" if usable else "no"
        modality = "vision" if model.vision else "text/code"
        configuration = "configured" if configured else "missing OPENROUTER_API_KEY"
        print(
            f"  [{marker:<5}] {model.label}\n"
            f"          {model.resolved_model()}  {modality}; {configuration}; {state}"
        )

    print(
        f"OpenRouter models usable now: {ready_count}/{len(models)}"
        + (" (using static fallback where possible)" if refresh_error else "")
    )


def save_history(runner: Any) -> Path:
    """Save history under uppercase H, replacing the debugger's old lowercase w."""
    level_root = (
        runner.tree_store.level_root
        if runner.tree_store
        else runner.tree_root
        / runner.game_id
        / f"level_{runner.current_level_label()}"
    )
    output = runner.save_history(
        histories_root(level_root) / f"{runner.game_id}_history.json"
    )
    print(f"Saved history: {output}")
    return Path(output)


def _remember_workflow_selection() -> None:
    """Remember every workflow execution so lowercase w can repeat it."""
    from llm_workflows import LlmWorkflowEngine

    current = LlmWorkflowEngine.run
    if getattr(current, "_arc3_remembers_workflow", False):
        return
    original = current

    def run(self: Any, workflow_id: str) -> None:
        self.runner._last_llm_workflow_id = workflow_id
        original(self, workflow_id)

    run._arc3_remembers_workflow = True  # type: ignore[attr-defined]
    LlmWorkflowEngine.run = run


def install_llm_key_controls(ui_module: Any) -> None:
    """Install the agreed top-level LLM keys and their unified help text."""
    _remember_workflow_selection()
    if getattr(ui_module.read_key, "_arc3_llm_key_controls", False):
        return

    original_read_key = ui_module.read_key
    original_print_controls = ui_module.print_controls

    def read_key() -> str:
        key = original_read_key()
        handlers = {
            "b": run_checked_batch,
            "w": repeat_last_workflow,
            "O": refresh_openrouter_models,
            "H": save_history,
        }
        handler = handlers.get(key)
        if handler is None:
            return key
        runner = _runner()
        if runner is None:
            print("No active ARC3 runner is available for this command.")
        else:
            try:
                handler(runner)
            except Exception as exc:
                print(f"LLM key {key!r} failed: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            original_print_controls(runner, rows)
        text = captured.getvalue().replace(
            "Files: (w) Save History  (e) Export State  (q) Quit",
            "Files: (H) Save History  (e) Export State  (q) Quit",
        )
        print(text, end="")
        print(
            "LLM keys: (g) Next Model  (G) Catalog/Batch Editor  "
            "(2/3/4) Light/Deep/Extreme"
        )
        print(
            "LLM run:  (b) Run Batch  (W) Choose Workflow  "
            "(w) Repeat Workflow  (O) Refresh OpenRouter"
        )

    read_key._arc3_llm_key_controls = True  # type: ignore[attr-defined]
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
