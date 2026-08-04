from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable

from arc3_runner import Arc3Runner
from gpt_bridge import GptArcAnalyzer
from llm_json_patch import install_llm_json_resilience
from llm_providers import ProviderSpec
from llm_transcripts import (
    finalize_last_transcript,
    list_transcripts,
    restore_transcript,
    transcript_metadata,
)
from project_paths import prompts_path
from unsloth_studio import StudioAwareLlmProviderRouter

install_llm_json_resilience()

_LAST_RUNNER: "MultiLlmArc3Runner | None" = None


class MultiLlmArc3Runner(Arc3Runner):
    """Arc3Runner whose existing GPT artifact path uses a provider router.

    The mutable `.pl` files remain the latest view. Every provider call also
    creates a restorable Markdown transcript containing an immutable artifact
    snapshot and the complete request/response debugging record.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._llm_router: StudioAwareLlmProviderRouter | None = None
        self._active_llm_analysis_level: int | None = None
        super().__init__(*args, **kwargs)
        global _LAST_RUNNER
        _LAST_RUNNER = self

    def llm_router(self) -> StudioAwareLlmProviderRouter:
        if self._llm_router is None:
            self._llm_router = StudioAwareLlmProviderRouter()
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

    @staticmethod
    def _provenance_path(node: Any):
        return node.path / "llm_provider.json"

    def _cached_provider_matches(self, node: Any, provider: ProviderSpec) -> bool:
        path = self._provenance_path(node)
        if not path.exists():
            return False
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return (
            value.get("provider_id") == provider.provider_id
            and value.get("model") == provider.resolved_model()
            and value.get("base_url") == provider.resolved_base_url()
        )

    def _write_provider_provenance(
        self,
        node: Any,
        provider: ProviderSpec,
        *,
        analysis_level: int,
    ) -> None:
        payload = {
            "provider_id": provider.provider_id,
            "label": provider.label,
            "adapter": provider.adapter,
            "model": provider.resolved_model(),
            "base_url": provider.resolved_base_url(),
            "analysis_level": analysis_level,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._provenance_path(node).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def gpt_command_1(self) -> None:
        """Restore a historical transcript or open the shared prompt editor."""
        store, node = self._require_node()
        transcripts = list_transcripts(node)
        print("\nLLM transcript cache for this state:")
        if not transcripts:
            print("  No completed transcript snapshots exist yet.")
        else:
            for index, path in enumerate(transcripts, start=1):
                metadata = transcript_metadata(path)
                active = ">" if index == 1 else " "
                print(
                    f" {active} {index:>2}. {path.name}\n"
                    f"       provider={metadata.get('provider_id')} "
                    f"model={metadata.get('model')} "
                    f"level={metadata.get('analysis_level')} "
                    f"profile={(metadata.get('analysis_profile') or {}).get('name')} "
                    f"tokens={metadata.get('max_output_tokens')}"
                )
        print("  [E] Edit shared LLM prompts  [Enter] Cancel")
        choice = input("Restore transcript number or E: ").strip()
        if not choice:
            print("Transcript selection cancelled.")
            return
        if choice.lower() in {"e", "edit", "prompts"}:
            self._analyzer().edit_prompts()
            return
        try:
            selected_index = int(choice) - 1
        except ValueError as error:
            raise RuntimeError("Enter a transcript number, E, or blank") from error
        if not 0 <= selected_index < len(transcripts):
            raise RuntimeError("Transcript number is out of range")
        selected = transcripts[selected_index]
        restored = restore_transcript(store, node, selected)
        print(f"Restored transcript: {selected}")
        for path in restored:
            print(f"  latest file: {path}")
        print(f"README.md now reflects: {selected.name}")

    def _run_gpt_analysis_level(self, level: int) -> None:
        store, node = self._require_node()
        provider = self.llm_router().current_spec()
        labels = {2: "demo", 3: "deep", 4: "extreme"}
        provider_changed = not self._cached_provider_matches(node, provider)
        force = level > 2 or provider_changed
        print(f"LLM provider: {self.current_llm_summary()}")
        if provider_changed:
            print("Provider/model differs from this node's cache; regenerating artifacts.")
        print(f"LLM {labels[level]} analysis (level {level}): {node.path}")
        self._active_llm_analysis_level = level
        try:
            result = self._analyzer().ensure_full_analysis(
                store,
                node,
                force=force,
                analysis_level=level,
            )
        except Exception as exc:
            transcript = finalize_last_transcript(store, node, error=str(exc))
            expected = (
                "object_registry.pl",
                "objects.pl",
                "differences.pl",
                "turtle_from_image.pl",
                "similarities.pl",
                "turtle_from_diff.pl",
                "rules.pl",
            )
            completed = [
                name
                for name in expected
                if (store.level_root / name).exists() or (node.path / name).exists()
            ]
            detail = ", ".join(completed) if completed else "none"
            transcript_note = f" Transcript: {transcript}." if transcript else ""
            raise RuntimeError(
                f"LLM level {level} analysis stopped using {provider.label}. "
                f"Files present: {detail}. Cause: {exc}.{transcript_note}"
            ) from exc
        finally:
            self._active_llm_analysis_level = None

        if any(
            result.get(key)
            for key in (
                "registry_called",
                "objects_called",
                "differences_called",
                "similarities_called",
                "turtle_from_image_called",
                "turtle_from_diff_called",
                "rules_called",
            )
        ):
            self._write_provider_provenance(
                node,
                provider,
                analysis_level=level,
            )

        transcript = finalize_last_transcript(store, node)
        ordered = (
            ("object_registry.pl", result["registry_path"], result["registry_called"]),
            ("objects.pl", result["objects_path"], result["objects_called"]),
            ("differences.pl", result["differences_path"], result["differences_called"]),
            (
                "turtle_from_image.pl",
                result["turtle_from_image_path"],
                result["turtle_from_image_called"],
            ),
            ("similarities.pl", result["similarities_path"], result["similarities_called"]),
            (
                "turtle_from_diff.pl",
                result["turtle_from_diff_path"],
                result["turtle_from_diff_called"],
            ),
            ("rules.pl", result["rules_path"], result["rules_called"]),
        )
        for label, path, called in ordered:
            if path is None:
                print(f"{label}: not applicable at level root")
            else:
                print(f"{label}: {path} ({'generated' if called else 'cached'})")
        print(f"llm_provider.json: {self._provenance_path(node)}")
        if transcript is not None:
            print(f"LLM comparison transcript: {transcript}")
        print(f"README.md: {node.readme_path}")
        print(f"LLM level {level} analysis complete.")

    def _run_targeted_llm_command(
        self,
        analysis_level: int,
        operation: Callable[[], None],
    ) -> None:
        store, node = self._require_node()
        self._active_llm_analysis_level = analysis_level
        try:
            operation()
        except Exception as exc:
            finalize_last_transcript(store, node, error=str(exc))
            raise
        finally:
            self._active_llm_analysis_level = None
        self._write_provider_provenance(
            node,
            self.llm_router().current_spec(),
            analysis_level=analysis_level,
        )
        transcript = finalize_last_transcript(store, node)
        if transcript is not None:
            print(f"LLM comparison transcript: {transcript}")

    def gpt_command_5(self) -> None:
        self._run_targeted_llm_command(5, super().gpt_command_5)

    def gpt_command_6(self) -> None:
        self._run_targeted_llm_command(6, super().gpt_command_6)


def last_runner() -> MultiLlmArc3Runner | None:
    return _LAST_RUNNER


def install_interactive_runner(ui_module: Any) -> None:
    """Install multi-LLM behavior without duplicating the debugger UI loop."""
    ui_module.Arc3Runner = MultiLlmArc3Runner
    ui_module.CONTROL_MODES["gpt"]["title"] = "LLM"
    ui_module.CONTROL_MODES["gpt"][1] = "Cached transcripts / edit shared prompts"

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
                    print("LLM provider list:")
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
