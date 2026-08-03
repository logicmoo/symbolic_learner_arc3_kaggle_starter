from __future__ import annotations

from typing import Any

from arc3_runner import Arc3Runner
from gpt_bridge import GptArcAnalyzer
from llm_providers import LlmProviderRouter, ProviderSpec
from project_paths import prompts_path

_LAST_RUNNER: "MultiLlmArc3Runner | None" = None


class MultiLlmArc3Runner(Arc3Runner):
    """Arc3Runner whose existing GPT artifact path uses a provider router.

    The action-tree, prompts, cache policy, and generated Prolog artifacts stay
    in GptArcAnalyzer. Only the final multimodal LLM request is routed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._llm_router: LlmProviderRouter | None = None
        super().__init__(*args, **kwargs)
        global _LAST_RUNNER
        _LAST_RUNNER = self

    def llm_router(self) -> LlmProviderRouter:
        if self._llm_router is None:
            self._llm_router = LlmProviderRouter()
        return self._llm_router

    def _analyzer(self) -> GptArcAnalyzer:
        if self._gpt_analyzer is None:
            self._gpt_analyzer = GptArcAnalyzer(
                prompts_path(),
                model="provider-selected",
                client=self.llm_router(),
            )
        return self._gpt_analyzer

    def cycle_llm_provider(self) -> ProviderSpec:
        return self.llm_router().cycle()

    def current_llm_summary(self) -> str:
        return self.llm_router().describe_current()

    def _run_gpt_analysis_level(self, level: int) -> None:
        print(f"LLM provider: {self.current_llm_summary()}")
        super()._run_gpt_analysis_level(level)


def last_runner() -> MultiLlmArc3Runner | None:
    return _LAST_RUNNER


def install_interactive_runner(ui_module: Any) -> None:
    """Install multi-LLM behavior without duplicating the debugger UI loop."""
    ui_module.Arc3Runner = MultiLlmArc3Runner
    ui_module.CONTROL_MODES["gpt"]["title"] = "LLM"

    original_print_controls = ui_module.print_controls
    original_print_mode_menu = ui_module.print_mode_menu

    def print_controls(
        runner: MultiLlmArc3Runner,
        rows: list[dict[str, Any]],
    ) -> None:
        original_print_controls(runner, rows)
        print("LLM: press (g) repeatedly to select the next configured provider")

    def print_mode_menu(mode: str) -> None:
        if mode == "gpt":
            runner = last_runner()
            if runner is not None:
                try:
                    selected = runner.cycle_llm_provider()
                    print(
                        f"\nSelected LLM: {selected.label} [{selected.provider_id}] "
                        f"model={selected.resolved_model()}"
                    )
                    print("Configured provider list:")
                    for status in runner.llm_router().statuses(probe=True):
                        marker = ">" if status.provider_id == selected.provider_id else " "
                        endpoint = f" @ {status.base_url}" if status.base_url else ""
                        print(
                            f" {marker} {status.provider_id:<10} "
                            f"{status.label:<24} {status.state}; "
                            f"model={status.model}{endpoint}"
                        )
                except Exception as exc:
                    print(f"\nUnable to select an LLM provider: {exc}")
        original_print_mode_menu(mode)

    ui_module.print_controls = print_controls
    ui_module.print_mode_menu = print_mode_menu
