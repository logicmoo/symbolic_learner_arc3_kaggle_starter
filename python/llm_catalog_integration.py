from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from llm_batch_profiles import _install_sampling_parameters
from llm_model_catalog import CatalogAwareLlmProviderRouter
from project_paths import prompts_path


def install_catalog_runner() -> None:
    """Install model/profile semantics onto MultiLlmArc3Runner."""
    from multillm_runner import MultiLlmArc3Runner

    if getattr(MultiLlmArc3Runner, "_arc3_catalog_installed", False):
        return

    original_run = MultiLlmArc3Runner._run_gpt_analysis_level

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
                label=model.label,
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

    MultiLlmArc3Runner.llm_router = llm_router
    MultiLlmArc3Runner.reload_llm_router = reload_llm_router
    MultiLlmArc3Runner.cycle_llm_provider = cycle_llm_provider
    MultiLlmArc3Runner.llm_provider_statuses = llm_provider_statuses
    MultiLlmArc3Runner.current_llm_summary = current_llm_summary
    MultiLlmArc3Runner._run_gpt_analysis_level = run_gpt_analysis_level
    MultiLlmArc3Runner._arc3_catalog_installed = True
    _install_sampling_parameters()
