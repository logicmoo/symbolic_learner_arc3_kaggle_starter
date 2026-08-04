from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

from llm_model_catalog import CatalogAwareLlmProviderRouter, ProfileDefinition


def install_profile_environment() -> None:
    current = CatalogAwareLlmProviderRouter.profile_environment
    if getattr(current, "_arc3_preserves_model_override", False):
        return

    @contextmanager
    def profile_environment(
        self: CatalogAwareLlmProviderRouter,
        profile: ProfileDefinition | str | None = None,
    ) -> Iterator[None]:
        selected = (
            self.profile_by_id[profile]
            if isinstance(profile, str)
            else profile or self.profile_for_spec()
        )
        model = self.model_by_id[selected.model_id]
        resolved_model = model.resolved_model()
        prefix = f"ARC3_GPT_{selected.analysis_level}_"
        values: dict[str, Any] = {
            prefix + "MAX_OUTPUT_TOKENS": selected.max_output_tokens,
            prefix + "REASONING_EFFORT": selected.reasoning_effort,
            prefix + "IMAGE_DETAIL": selected.current_image_detail,
            prefix + "PARENT_IMAGE_DETAIL": selected.parent_image_detail,
            "ARC3_LLM_TEMPERATURE": selected.temperature,
            "ARC3_LLM_TOP_P": selected.top_p,
            "ARC3_LLM_SEED": selected.seed,
            "ARC3_LLM_TIMEOUT_SECONDS": selected.timeout_seconds,
        }
        if model.model_env:
            values[model.model_env] = resolved_model

        previous: dict[str, str | None] = {}
        try:
            for name, value in values.items():
                previous[name] = os.environ.get(name)
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = str(value)
            yield
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    profile_environment._arc3_preserves_model_override = True  # type: ignore[attr-defined]
    CatalogAwareLlmProviderRouter.profile_environment = profile_environment
