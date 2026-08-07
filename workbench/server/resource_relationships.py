from __future__ import annotations

from typing import Any


def relationship_ids(value: Any) -> list[str]:
    """Normalize a persisted relationship pointer to a list of resource IDs.

    Scalars remain readable for compatibility, but new and edited resources use
    arrays so every relationship can be many-to-many.
    """
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return list(dict.fromkeys(str(item) for item in value if str(item).strip()))
    return []


def points_to(document: dict[str, Any], field: str, resource_id: str) -> bool:
    return resource_id in relationship_ids(document.get(field))
