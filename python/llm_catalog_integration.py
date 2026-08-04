from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from llm_catalog_sampling import install_profile_sampling
from llm_model_catalog import CatalogAwareLlmProviderRouter
from project_paths import prompts_path


def _install_catalog_prompt_compatibility() -> None:
    from gpt_bridge import GptArcAnalyzer

    current = GptArcAnalyzer.prompts
    if getattr(current, "_arc3_catalog_prompts", False):
        return
    original = current

    def prompts(self: GptArcAnalyzer) -> dict[str, str]:
        raw = json.loads(self.prompts_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("llm_profiles"), list):
            return original(self)
        sections = {
            str(key): self._normalize_prompt(value, key=str(key))
            for key, value in (raw.get("prompt_text") or {}).items()
        }
        profile_id = str(raw.get("default_profile") or "").strip()
        profile = next(
            (
                item
                for item in raw["llm_profiles"]
                if isinstance(item, dict) and str(item.get("id") or "") == profile_id
            ),
            raw["llm_profiles"][0],
        )
        names = profile.get("prompt_text") if isinstance(profile, dict) else None
        if not isinstance(names, list) or not names:
            raise ValueError("Selected LLM profile has no prompt_text list")
        missing = [str(name) for name in names if str(name) not in sections]
        if missing:
            raise ValueError("Unknown prompt_text sections: " + ", ".join(missing))
        return {
            "combined": "\n\n".join(sections[str(name)] for name in names).strip()
        }

    prompts._arc3_catalog_prompts = True  # type: ignore[attr-defined]
    GptArcAnalyzer.prompts = prompts


def _install_catalog_transcript_metadata() -> None:
    import llm_json_patch
    import llm_transcripts

    current = llm_json_patch.begin_transcript
    if getattr(current, "_arc3_catalog_metadata", False):
        return
    original = current

    def begin_transcript(router: Any, request: Any):
        run = original(router, request)
        if run is None or not isinstance(router, CatalogAwareLlmProviderRouter):
            return run
        spec = router.current_spec()
        profile = router.profile_for_spec(spec)
        model = router.model_for_profile(profile)
        backend = router.backend_for_profile(profile)
        run.metadata.update(
            {
                "backend_id": backend.backend_id,
                "backend_label": backend.label,
                "model_id": model.model_id,
                "model_label": model.label,
                "profile_id": profile.profile_id,
                "profile_label": profile.label,
                "single_enabled": profile.single_enabled,
                "batch_enabled": profile.batch_enabled,
            }
        )
        return run

    begin_transcript._arc3_catalog_metadata = True  # type: ignore[attr-defined]
    llm_json_patch.begin_transcript = begin_transcript
    llm_transcripts.begin_transcript = begin_transcript


def install_catalog_runner() -> None:
    """Install model/profile semantics onto MultiLlmArc3Runner."""
    from multillm_runner import MultiLlmArc3Runner

    if getattr(MultiLlmArc3Runner, "_arc3_catalog_installed", False):
        return

    original_run = MultiLlmArc3Runner._run_gpt_analysis_level
    original_provenance = MultiLlmArc3Runner._write_provider_provenance

    def llm_router(self: Any) -> CatalogAwareLlmProviderRouter:
        if self._llm_router is None:
            self._llm_router = CatalogAwareLlmProviderRouter(prompts_path())
        return self._llm_router

    def reload_llm_router(
        self: Any,
        *,
        active_model_id: str | None = None,
    ) -> CatalogAwareLlmProviderRouter:
        old = self._llm_router
        if active_model_id is None and isinstance(old, CatalogAwareLlmProviderRouter):
            active_model_id = old.active_model().model_id
        self._llm_router = CatalogAwareLlmProviderRouter(prompts_path())
        self._gpt_analyzer = None
        if active_model_id:
            try:
                self._llm_router.select_model(active_model_id)
            except Exception:
                pass
        return self._llm_router

    def cycle_llm_provider(self: Any):
        router = self.llm_router()
        model_ids = list(router.configured_model_ids())
        if not model_ids:
            raise RuntimeError("No configured single-run LLM models")
        current = router.active_model().model_id
        start = model_ids.index(current) + 1 if current in model_ids else 0
        failures: list[str] = []
        for offset in range(len(model_ids)):
            model_id = model_ids[(start + offset) % len(model_ids)]
            profile = router.default_profile_for_model(model_id)
            spec = next(
                item for item in router.specs if item.provider_id == profile.profile_id
            )
            ready, state = self._provider_readiness(spec)
            if ready:
                return router.select_model(model_id)
            failures.append(f"{model_id}: {state}")
        raise RuntimeError(
            "No configured single-run LLM model is currently ready ("
            + "; ".join(failures)
            + ")"
        )

    def llm_provider_statuses(
        self: Any,
        *,
        refresh: bool = False,
    ) -> tuple[dict[str, Any], ...]:
        router = self.llm_router()
        active_model_id = router.active_model().model_id
        rows: list[dict[str, Any]] = []
        for model in router.models:
            profiles = [
                profile
                for profile in router.profiles_for_model(model.model_id)
                if profile.single_enabled
            ]
            if not profiles:
                continue
            representative = router.default_profile_for_model(model.model_id)
            spec = next(
                item
                for item in router.specs
                if item.provider_id == representative.profile_id
            )
            ready, state = self._provider_readiness(spec, refresh=refresh)
            backend = router.backend_by_id[model.provider_id]
            display = SimpleNamespace(
                provider_id=model.model_id,
                label=f"{model.label} via {backend.label}",
                resolved_model=model.resolved_model,
                resolved_base_url=spec.resolved_base_url,
            )
            rows.append(
                {
                    "provider": display,
                    "ready": ready,
                    "state": state,
                    "active": model.model_id == active_model_id,
                    "model": model,
                    "backend": backend,
                    "profile": representative,
                }
            )
        return tuple(rows)

    def current_llm_summary(self: Any) -> str:
        return self.llm_router().describe_current()

    def run_gpt_analysis_level(
        self: Any,
        level: int,
        *,
        profile_id: str | None = None,
        mode: str = "single",
    ) -> None:
        router = self.llm_router()
        if profile_id is None:
            router.activate_level(level, mode=mode)
        else:
            profile = router.profile_by_id[profile_id]
            if profile.analysis_level != level:
                raise RuntimeError(
                    f"Profile {profile_id} is level {profile.analysis_level}, not {level}"
                )
            router.select_profile(profile_id, mode=mode)
        profile = router.profile_for_spec()
        with router.profile_environment(profile):
            original_run(self, level)

    def write_provider_provenance(
        self: Any,
        node: Any,
        provider: Any,
        *,
        analysis_level: int,
    ) -> None:
        original_provenance(
            self,
            node,
            provider,
            analysis_level=analysis_level,
        )
        router = self.llm_router()
        profile = router.profile_for_spec(provider)
        model = router.model_for_profile(profile)
        backend = router.backend_for_profile(profile)
        path = self._provenance_path(node)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.update(
            {
                "backend_id": backend.backend_id,
                "backend_label": backend.label,
                "model_id": model.model_id,
                "model_label": model.label,
                "profile_id": profile.profile_id,
                "profile_label": profile.label,
                "single_enabled": profile.single_enabled,
                "batch_enabled": profile.batch_enabled,
            }
        )
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    MultiLlmArc3Runner.llm_router = llm_router
    MultiLlmArc3Runner.reload_llm_router = reload_llm_router
    MultiLlmArc3Runner.cycle_llm_provider = cycle_llm_provider
    MultiLlmArc3Runner.llm_provider_statuses = llm_provider_statuses
    MultiLlmArc3Runner.current_llm_summary = current_llm_summary
    MultiLlmArc3Runner._run_gpt_analysis_level = run_gpt_analysis_level
    MultiLlmArc3Runner._write_provider_provenance = write_provider_provenance
    MultiLlmArc3Runner._arc3_catalog_installed = True
    install_profile_sampling()
    _install_catalog_prompt_compatibility()
    _install_catalog_transcript_metadata()
