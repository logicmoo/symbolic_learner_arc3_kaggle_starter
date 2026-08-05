from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4

from worldworkbench.core import Intervention, Observation, SimulationRequest


def _jsonable(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.name
    if is_dataclass(value):
        return _jsonable(asdict(value), depth + 1)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item, depth + 1) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item, depth + 1) for item in value]
    for method_name in ("model_dump", "dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                return _jsonable(method(), depth + 1)
            except Exception:
                pass
    return repr(value)


class Arc3ObservationAdapter:
    """Translate an Arc3Runner state into a domain-neutral observation."""

    def capture(self, runner: Any, *, observation_id: str | None = None) -> Observation:
        node = getattr(runner, "current_node", None)
        image_path = getattr(node, "image_path", None)
        metadata = {
            "adapter": "arc3",
            "environment_id": str(getattr(runner, "game_id", "unknown")),
            "episode": int(getattr(runner, "detected_level", 1)),
            "state": runner.state_name() if callable(getattr(runner, "state_name", None)) else None,
            "frame_path": str(image_path) if image_path else None,
            "tree_node": str(getattr(node, "path", "")) if node else None,
        }
        return Observation(
            observation_id=observation_id or f"arc3-{uuid4().hex[:12]}",
            payload=_jsonable(getattr(runner, "current_observation", None)),
            source=f"arc3:{metadata['environment_id']}",
            representation_type="arc3_state",
            metadata=metadata,
        )


class Arc3InterventionAdapter:
    """Apply a selected workbench intervention through an Arc3Runner."""

    def apply(self, runner: Any, request: SimulationRequest) -> Any:
        intervention = dict(request.intervention)
        try:
            action = intervention.pop("action")
        except KeyError as exc:
            raise ValueError("ARC3 intervention requires an 'action'") from exc
        data = intervention.pop("data", None)
        if data is not None and not isinstance(data, Mapping):
            raise ValueError("ARC3 intervention 'data' must be a mapping")
        return runner.step(action, data=dict(data or {}), **intervention)

    def apply_human_choice(
        self,
        runner: Any,
        action: Any,
        *,
        data: Mapping[str, Any] | None = None,
        intervention_id: str | None = None,
    ) -> tuple[Intervention, Observation]:
        """Apply a human-selected ARC3 action and capture its resulting state."""
        runner.step(action, data=dict(data or {}))
        observed = Intervention(
            intervention_id=intervention_id or f"human-{uuid4().hex[:12]}",
            actor="human",
            action=str(getattr(action, "name", action)),
            parameters={"data": dict(data or {})},
        )
        return observed, Arc3ObservationAdapter().capture(runner)


def arc3_artifact_metadata(runner: Any) -> dict[str, str | None]:
    """Return portable links to the current ARC3 evidence artifacts."""

    node = getattr(runner, "current_node", None)
    tree_store = getattr(runner, "tree_store", None)
    return {
        "analysis_node": str(getattr(node, "path", "")) if node else None,
        "observation_image": str(getattr(node, "image_path", "")) if node else None,
        "world_identity_registry": (
            str(getattr(tree_store, "object_registry_path", "")) if tree_store else None
        ),
    }
