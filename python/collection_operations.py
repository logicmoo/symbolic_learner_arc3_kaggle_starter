from __future__ import annotations

import random
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any


def random_list_element(items: Sequence[Any], seed: int | None = None) -> Any:
    """Return one real element from a non-empty sequence."""
    if not items:
        raise ValueError("cannot choose from an empty list")
    return random.Random(seed).choice(list(items))


def curate_gallery_resource(
    items: Sequence[Any],
    label: str = "Gallery Resource",
    title_field: str = "title",
    image_field: str = "frame_path",
    description_field: str = "description",
) -> dict[str, Any]:
    """Neutrally assemble any collection into one human/AI Gallery Resource."""
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        source = dict(item) if isinstance(item, dict) else {"value": item}
        preview = source.get("preview") if isinstance(source.get("preview"), dict) else {}
        title = source.get(title_field) or source.get("label") or source.get("id") or f"Item {index + 1}"
        image = source.get(image_field) or preview.get(image_field) or preview.get("frame_path")
        entries.append({
            "index": index,
            "title": str(title),
            "description": str(source.get(description_field) or ""),
            "image": image,
            "source": source,
        })
    return {
        "kind": "gallery_resource",
        "label": label,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "count": len(entries),
        "entries": entries,
        "items": list(items),
    }
