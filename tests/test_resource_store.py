from __future__ import annotations

from pathlib import Path

import pytest

from resource_store import FilesystemProvider, get_filesystem_provider


def test_singleton_provider_delegates_json_files_to_disk(tmp_path: Path) -> None:
    provider = get_filesystem_provider()
    target = tmp_path / "design" / "operations" / "example.operation.json"
    provider.write_json(target, {"kind": "operation", "id": "example"})

    assert provider.read_json(target) == {"kind": "operation", "id": "example"}
    assert provider.glob(tmp_path, ["design/operations"]) == [target]
    assert provider is get_filesystem_provider()
    metrics = provider.metrics()
    assert metrics["write"] >= 1
    assert metrics["read"] >= 1
    assert metrics["scan"] >= 1
    assert metrics["suffix:.json"] >= 2


def test_provider_rejects_escaping_logical_paths(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    with pytest.raises(ValueError, match="escapes provider root"):
        provider.resolve(tmp_path, "../outside.json")
