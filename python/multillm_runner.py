from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

from arc3_runner import Arc3Runner
from gpt_bridge import GptArcAnalyzer
from llm_json_patch import install_llm_json_resilience
from llm_providers import ProviderSpec
from llm_readme_patch import transcript_is_restorable
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

    Pressing ``g`` advances to the next provider that is both configured and
    reachable. A provider that fails an ARC3 analysis is skipped for the rest
    of the current debugger session, making repeated ``g 4`` runs useful for
    collecting independent provider outputs without repeatedly hitting a bad
    key, offline endpoint, unavailable model, or exhausted free-tier service.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._llm_router: StudioAwareLlmProviderRouter | None = None
        self._active_llm_analysis_level: int | None = None
        self._llm_probe_cache: dict[str, tuple[float, bool, str]] = {}
        self._llm_session_failures: dict[str, str] = {}
        self._llm_urlopen: Callable[..., Any] = urllib.request.urlopen
        super().__init__(*args, **kwargs)
        global _LAST_RUNNER
        _LAST_RUNNER = self

    def llm_router(self) -> StudioAwareLlmProviderRouter:
        if self._llm_router is None:
            self._llm_router = StudioAwareLlmProviderRouter(prompts_path())
        return self._llm_router

    def _analyzer(self) -> GptArcAnalyzer:
        if self._gpt_analyzer is None:
            self._gpt_analyzer = GptArcAnalyzer(
                prompts_path(),
                model="provider-selected",
                client=self.llm_router(),
            )
        return self._gpt_analyzer

    @staticmethod
    def _float_environment(name: str, default: float) -> float:
        try:
            return max(0.0, float(os.environ.get(name, str(default))))
        except ValueError:
            return default

    @staticmethod
    def _provider_probe_url(provider: ProviderSpec) -> str | None:
        health_url = provider.resolved_health_url()
        if health_url:
            return health_url
        base_url = provider.resolved_base_url()
        if not base_url:
            return None
        return base_url if base_url.endswith("/models") else base_url + "/models"

    @staticmethod
    def _provider_probe_headers(provider: ProviderSpec) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        api_key = provider.resolved_api_key()
        if not api_key:
            return headers
        if provider.adapter == "anthropic_messages":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = provider.anthropic_version
        else:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _provider_readiness(
        self,
        provider: ProviderSpec,
        *,
        refresh: bool = False,
    ) -> tuple[bool, str]:
        configured, configuration_state = provider.configuration_state()
        if not configured:
            return False, configuration_state

        prior_failure = self._llm_session_failures.get(provider.provider_id)
        if prior_failure:
            return False, f"failed this session: {prior_failure}"

        now = time.monotonic()
        ttl = self._float_environment("ARC3_LLM_PROBE_TTL", 60.0)
        cached = self._llm_probe_cache.get(provider.provider_id)
        if not refresh and cached is not None and now - cached[0] <= ttl:
            return cached[1], cached[2]

        probe_url = self._provider_probe_url(provider)
        if not probe_url:
            result = (True, "configured; no readiness URL")
            self._llm_probe_cache[provider.provider_id] = (now, *result)
            return result

        request = urllib.request.Request(
            probe_url,
            headers=self._provider_probe_headers(provider),
        )
        timeout = self._float_environment("ARC3_LLM_PROBE_TIMEOUT", 1.5)
        try:
            with self._llm_urlopen(request, timeout=timeout) as response:
                status = int(getattr(response, "status", 200))
                result = (
                    200 <= status < 300,
                    "ready" if 200 <= status < 300 else f"HTTP {status}",
                )
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace").strip()
            except Exception:
                detail = ""
            suffix = f": {detail[:160]}" if detail else ""
            result = (False, f"HTTP {exc.code}{suffix}")
        except urllib.error.URLError as exc:
            result = (False, str(exc.reason))
        except TimeoutError:
            result = (False, "timeout")
        except Exception as exc:
            result = (False, str(exc))

        self._llm_probe_cache[provider.provider_id] = (now, *result)
        return result

    def llm_provider_statuses(
        self,
        *,
        refresh: bool = False,
    ) -> tuple[dict[str, Any], ...]:
        router = self.llm_router()
        active_id = getattr(router, "_active_id", None)
        rows: list[dict[str, Any]] = []
        for provider in router.specs:
            ready, state = self._provider_readiness(provider, refresh=refresh)
            rows.append(
                {
                    "provider": provider,
                    "ready": ready,
                    "state": state,
                    "active": provider.provider_id == active_id,
                }
            )
        return tuple(rows)

    def cycle_llm_provider(self) -> ProviderSpec:
        router = self.llm_router()
        configured = list(router.configured_specs())
        if not configured:
            reasons = ", ".join(
                f"{provider.provider_id}: {provider.configuration_state()[1]}"
                for provider in router.specs
            )
            raise RuntimeError(f"No configured LLM providers ({reasons})")

        active_id = getattr(router, "_active_id", None)
        if active_id is None:
            start = next(
                (
                    index
                    for index, provider in enumerate(configured)
                    if provider.provider_id == router.default_provider
                ),
                0,
            )
        else:
            current_index = next(
                (
                    index
                    for index, provider in enumerate(configured)
                    if provider.provider_id == active_id
                ),
                -1,
            )
            start = (current_index + 1) % len(configured)

        attempted: list[str] = []
        for offset in range(len(configured)):
            provider = configured[(start + offset) % len(configured)]
            ready, state = self._provider_readiness(provider)
            if ready:
                return router.select(provider.provider_id)
            attempted.append(f"{provider.provider_id}: {state}")

        raise RuntimeError(
            "No configured LLM provider is currently ready ("
            + "; ".join(attempted)
            + ")"
        )

    def _mark_llm_provider_failed(
        self,
        provider: ProviderSpec,
        error: BaseException,
    ) -> None:
        detail = " ".join(str(error).split()) or error.__class__.__name__
        self._llm_session_failures[provider.provider_id] = detail[:240]
        self._llm_probe_cache.pop(provider.provider_id, None)

    def _mark_llm_provider_succeeded(self, provider: ProviderSpec) -> None:
        self._llm_session_failures.pop(provider.provider_id, None)
        self._llm_probe_cache[provider.provider_id] = (
            time.monotonic(),
            True,
            "ready; completed ARC3 analysis",
        )

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
            "prompt_text": list(self.llm_router().prompt_section_names(provider)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._provenance_path(node).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def gpt_command_1(self) -> None:
        """Restore a historical transcript or open the unified LLM config."""
        store, node = self._require_node()
        transcripts = list_transcripts(node)
        active = next(
            (path for path in transcripts if transcript_is_restorable(path)),
            None,
        )
        print("\nLLM transcript cache for this state:")
        if not transcripts:
            print("  No transcript records exist yet.")
        else:
            for index, path in enumerate(transcripts, start=1):
                metadata = transcript_metadata(path)
                restorable = transcript_is_restorable(path)
                marker = ">" if active is not None and path.resolve() == active.resolve() else " "
                kind = "restorable" if restorable else "debug-only"
                print(
                    f" {marker} {index:>2}. {path.name}\n"
                    f"       kind={kind} status={metadata.get('status')} "
                    f"provider={metadata.get('provider_id')} "
                    f"model={metadata.get('model')} "
                    f"level={metadata.get('analysis_level')} "
                    f"profile={(metadata.get('analysis_profile') or {}).get('name')} "
                    f"tokens={metadata.get('max_output_tokens')}"
                )
        print("  [E] Edit unified providers/prompt_text config  [Enter] Cancel")
        choice = input("Restore transcript number or E: ").strip()
        if not choice:
            print("Transcript selection cancelled.")
            return
        if choice.lower() in {"e", "edit", "prompts", "config"}:
            self._analyzer().edit_prompts()
            return
        try:
            selected_index = int(choice) - 1
        except ValueError as error:
            raise RuntimeError("Enter a transcript number, E, or blank") from error
        if not 0 <= selected_index < len(transcripts):
            raise RuntimeError("Transcript number is out of range")
        selected = transcripts[selected_index]
        if not transcript_is_restorable(selected):
            raise RuntimeError(
                f"Transcript is debug-only and has no completed artifact snapshot: {selected.name}"
            )
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
            self._mark_llm_provider_failed(provider, exc)
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
                f"This provider will be skipped by subsequent g presses in this session. "
                f"Files present: {detail}. Cause: {exc}.{transcript_note}"
            ) from exc
        finally:
            self._active_llm_analysis_level = None

        self._mark_llm_provider_succeeded(provider)
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
        provider = self.llm_router().current_spec()
        self._active_llm_analysis_level = analysis_level
        try:
            operation()
        except Exception as exc:
            self._mark_llm_provider_failed(provider, exc)
            finalize_last_transcript(store, node, error=str(exc))
            raise
        finally:
            self._active_llm_analysis_level = None
        self._mark_llm_provider_succeeded(provider)
        self._write_provider_provenance(
            node,
            provider,
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
    ui_module.CONTROL_MODES["gpt"][1] = "Cached transcripts / edit unified config"

    original_print_controls = ui_module.print_controls
    original_print_mode_menu = ui_module.print_mode_menu

    def print_controls(
        runner: MultiLlmArc3Runner,
        rows: list[dict[str, Any]],
    ) -> None:
        original_print_controls(runner, rows)
        print("LLM: (g) next configured+ready provider; then (2/3/4) saves its transcript")
        print("Compare providers by repeating: g 4, g 4, g 4 ...")

    def print_mode_menu(mode: str) -> None:
        if mode == "gpt":
            runner = last_runner()
            if runner is not None:
                try:
                    selected = runner.cycle_llm_provider()
                    prompt_names = ",".join(
                        runner.llm_router().prompt_section_names(selected)
                    )
                    print(
                        f"\nSelected LLM: {selected.label} [{selected.provider_id}] "
                        f"model={selected.resolved_model()} "
                        f"prompt_text=[{prompt_names}]"
                    )
                    print("LLM provider list (missing, offline, and session-failed providers are skipped):")
                    for row in runner.llm_provider_statuses():
                        provider = row["provider"]
                        marker = ">" if row["active"] else " "
                        endpoint = (
                            f" @ {provider.resolved_base_url()}"
                            if provider.resolved_base_url()
                            else ""
                        )
                        print(
                            f" {marker} {provider.provider_id:<18} "
                            f"{provider.label:<42} {row['state']}; "
                            f"model={provider.resolved_model()}{endpoint}"
                        )
                    print("Press 4 to save this provider's extreme output, then g for the next one.")
                except Exception as exc:
                    print(f"\nUnable to select an LLM provider: {exc}")
        original_print_mode_menu(mode)

    ui_module.print_controls = print_controls
    ui_module.print_mode_menu = print_mode_menu
