from __future__ import annotations

from pathlib import Path
import re

import pytest

from resource_store import FilesystemProvider, get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]


def test_singleton_provider_delegates_json_files_to_disk(tmp_path: Path) -> None:
    provider = get_filesystem_provider()
    target = tmp_path / "design" / "operations" / "example.operation.json"
    provider.write_json(target, {"kind": "operation", "id": "example"})

    assert not target.exists()
    assert target.with_suffix(".metta").is_file()
    assert provider.read_json(target) == {"kind": "operation", "id": "example"}
    assert provider.glob(tmp_path, ["design/operations"]) == [target]
    assert provider is get_filesystem_provider()
    metrics = provider.metrics()
    assert metrics["write"] >= 1
    assert metrics["read"] >= 1
    assert metrics["scan"] >= 1
    assert metrics["suffix:.json"] >= 2


def test_provider_transparently_reads_existing_metta_through_json_path(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    logical = tmp_path / "nested.resource.json"
    physical = logical.with_suffix(".metta")
    physical.write_text('(\n  (kind resource)\n  (values ([]\n    1\n    "two words"\n    ()\n  ))\n)\n', encoding="utf-8")

    assert provider.exists(logical)
    assert provider.is_file(logical)
    assert provider.glob(tmp_path, ["."]) == [logical]
    assert provider.read_json(logical) == {"kind": "resource", "values": [1, "two words", {}]}


def test_provider_reads_multiple_resources_and_surgically_updates_one(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    logical = tmp_path / "combined.goal.json"
    physical = logical.with_suffix(".metta")
    first = "((kind goal) (id parent) (label Original))"
    sibling = "((kind goal_variant) (id child) (label \"Leave me exactly so\"))"
    physical.write_text(f"; header\n{first}\n\n; sibling formatting\n{sibling}\n", encoding="utf-8")

    assert [item["id"] for item in provider.read_json_documents(logical)] == ["parent", "child"]

    provider.write_text(logical, '{"kind":"goal","id":"parent","label":"Changed"}\n')

    updated = physical.read_text(encoding="utf-8")
    assert first not in updated
    assert "; header\n" in updated
    assert f"\n\n; sibling formatting\n{sibling}\n" in updated
    assert provider.read_json_documents(logical)[0]["label"] == "Changed"


def test_provider_accepts_json_arrays_and_consecutive_json_resources(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    array_path = tmp_path / "array.data"
    consecutive_path = tmp_path / "consecutive.data"
    array_path.write_text('[{"id":"one"},{"id":"two"}]', encoding="utf-8")
    consecutive_path.write_text('{"id":"one"}\n{"id":"two"}', encoding="utf-8")

    assert provider.read_json_documents(array_path) == [{"id": "one"}, {"id": "two"}]
    assert provider.read_json_documents(consecutive_path) == [{"id": "one"}, {"id": "two"}]


def test_provider_caches_unchanged_resource_parses_without_sharing_mutations(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    logical = tmp_path / "cached.resource.json"
    provider.write_json(logical, {"id": "cached", "values": [1]})

    first = provider.read_json_documents(logical)
    first[0]["values"].append(2)
    second = provider.read_json_documents(logical)

    assert second == [{"id": "cached", "values": [1]}]
    assert provider.metrics()["cache-hit"] == 1


def test_provider_invalidates_cache_on_write_and_external_file_change(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    logical = tmp_path / "changing.resource.json"
    provider.write_json(logical, {"id": "changing", "value": 1})
    assert provider.read_json(logical)["value"] == 1

    provider.write_json(logical, {"id": "changing", "value": 22})
    assert provider.read_json(logical)["value"] == 22

    logical.with_suffix(".metta").write_text("((id changing) (value 333))\n", encoding="utf-8")
    assert provider.read_json(logical)["value"] == 333


def test_provider_atomic_json_replacement_writes_metta(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    temporary = tmp_path / "model.json.tmp"
    target = tmp_path / "model.json"
    temporary.write_text('{"kind":"model","enabled":true}', encoding="utf-8")

    provider.replace(temporary, target)

    assert not temporary.exists()
    assert not target.exists()
    assert provider.read_json(target) == {"kind": "model", "enabled": True}


def test_provider_rejects_escaping_logical_paths(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    with pytest.raises(ValueError, match="escapes provider root"):
        provider.resolve(tmp_path, "../outside.json")


def test_provider_handles_text_binary_discovery_and_atomic_replacement(tmp_path: Path) -> None:
    provider = FilesystemProvider()
    docs = tmp_path / "docs"
    provider.make_directory(docs)
    markdown = docs / "guide.md"
    temporary = docs / "guide.tmp"
    provider.write_text(temporary, "# Guide\n")
    provider.replace(temporary, markdown)

    image = docs / "reference.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\n")

    assert provider.read_text(markdown) == "# Guide\n"
    assert provider.read_bytes(image).startswith(b"\x89PNG")
    assert provider.rglob(tmp_path, "*.md") == [markdown]
    ignored = tmp_path / "node_modules"
    provider.make_directory(ignored)
    provider.write_text(ignored / "dependency.md", "ignored")
    assert provider.rglob(tmp_path, "*.md", ignored_names={"node_modules"}) == [markdown]
    assert provider.iterdir(docs) == [markdown, image]
    assert provider.is_file(markdown)
    assert provider.is_dir(docs)
    assert provider.stat(markdown).st_size >= len("# Guide\n")


def test_running_server_resource_io_stays_behind_filesystem_provider() -> None:
    """Prevent application resource code from quietly bypassing the provider boundary."""
    forbidden = re.compile(
        r"\.(?:read_text|write_text|read_bytes|write_bytes|glob|rglob|iterdir|mkdir|unlink)\("
    )
    offenders: list[str] = []
    server = ROOT / "workbench" / "server"

    for path in sorted(server.glob("*.py")):
        if path.name == "resource_store.py" or path.name.startswith("test_"):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if (
                forbidden.search(line)
                and "resources." not in line
                and "get_filesystem_provider()." not in line
            ):
                offenders.append(f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}")

    assert offenders == [], "Direct resource filesystem access found:\n" + "\n".join(offenders)
