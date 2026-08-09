from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

from resource_store import get_filesystem_provider


def redact_secrets(value: Any, key: str = "") -> Any:
    if key and re.search(r"(?:authorization|api.?key|access.?token|secret|password)$", key, re.IGNORECASE):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(name): redact_secrets(item, str(name)) for name, item in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


def write_invocation_trace(workspace_root: Path, family: str, resource_id: str, kind: str, trace: dict[str, Any]) -> str:
    created = datetime.now(UTC)
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", resource_id).strip("._") or "resource"
    trace_id = f"{created.strftime('%Y%m%dT%H%M%S.%fZ')}_{safe_id}_{uuid4().hex[:8]}"
    relative_path = f"runtime/logs/{family}_invocations/{trace_id}.log"
    document = {**trace, "kind": kind, "id": trace_id, "createdAt": created.isoformat(), "logPath": relative_path}
    resources = get_filesystem_provider()
    resources.write_text(resources.resolve(workspace_root, relative_path), json.dumps(redact_secrets(document), indent=2, ensure_ascii=False, default=str) + "\n")
    return relative_path


def read_invocation_trace(workspace_root: Path, family: str, path: str) -> str:
    logical = PurePosixPath(path)
    expected = ("runtime", "logs", f"{family}_invocations")
    if logical.is_absolute() or ".." in logical.parts or logical.parts[:3] != expected or logical.suffix.lower() != ".log":
        raise ValueError(f"only {family} invocation debug logs can be read here")
    resources = get_filesystem_provider()
    resolved = resources.resolve(workspace_root, logical.as_posix())
    if not resources.is_file(resolved):
        raise FileNotFoundError(path)
    return resources.read_text(resolved)
