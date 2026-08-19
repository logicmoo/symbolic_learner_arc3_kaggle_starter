from pathlib import Path

import pytest
from fastapi import HTTPException

import workspace_api


def _make_workspace(tmp_path: Path, monkeypatch) -> str:
    workspace = tmp_path / "myws"
    workspace.mkdir()
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    return "myws"


def test_data_file_writes_json_verbatim_without_kind(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)
    payload = '{"state": "NOT_FINISHED", "level": "1"}'

    result = workspace_api.write_workspace_data_file(
        workspace_id,
        {"path": "data/level_1/state.json", "content": payload},
    )

    written = tmp_path / "myws" / "data" / "level_1" / "state.json"
    # The raw endpoint must not mangle the document: exact bytes, no injected "kind".
    assert written.read_text(encoding="utf-8") == payload
    assert '"kind"' not in written.read_text(encoding="utf-8")
    assert result["file"]["path"] == "data/level_1/state.json"
    assert result["file"]["content"] == payload


def test_data_file_accepts_eng_and_prompt_suffixes(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    workspace_api.write_workspace_data_file(
        workspace_id,
        {"path": "data/level_1/objects.eng", "content": "english rules"},
    )
    workspace_api.write_workspace_data_file(
        workspace_id,
        {"path": "data/level_1/remove.prompt", "content": "prompt body"},
    )

    assert (tmp_path / "myws" / "data" / "level_1" / "objects.eng").read_text(encoding="utf-8") == "english rules"
    assert (tmp_path / "myws" / "data" / "level_1" / "remove.prompt").read_text(encoding="utf-8") == "prompt body"


def test_data_file_creates_nested_directories(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    workspace_api.write_workspace_data_file(
        workspace_id,
        {"path": "data/level_1/LEFT/UP/state.json", "content": "{}"},
    )

    assert (tmp_path / "myws" / "data" / "level_1" / "LEFT" / "UP" / "state.json").read_text(encoding="utf-8") == "{}"


def test_data_file_rejects_disallowed_suffix(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        workspace_api.write_workspace_data_file(
            workspace_id,
            {"path": "data/level_1/image.png", "content": "not text"},
        )

    assert error.value.status_code == 400
    assert not (tmp_path / "myws" / "data" / "level_1" / "image.png").exists()


def test_data_file_requires_path(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        workspace_api.write_workspace_data_file(workspace_id, {"content": "x"})

    assert error.value.status_code == 400


def test_data_file_requires_string_content(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        workspace_api.write_workspace_data_file(
            workspace_id,
            {"path": "data/level_1/state.json", "content": {"not": "a string"}},
        )

    assert error.value.status_code == 400


def test_data_file_rejects_path_escape(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        workspace_api.write_workspace_data_file(
            workspace_id,
            {"path": "../escape.json", "content": "{}"},
        )

    assert error.value.status_code == 400


def test_line_counts_batches_non_blank_counts(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)
    base = tmp_path / "myws" / "data" / "level_1"
    base.mkdir(parents=True)
    (base / "objects.pl").write_text("a.\n\nb.\n   \nc.\n", encoding="utf-8")
    (base / "empty.pl").write_text("", encoding="utf-8")

    result = workspace_api.data_file_line_counts(
        workspace_id,
        {"paths": [
            "data/level_1/objects.pl",
            "data/level_1/empty.pl",
            "data/level_1/missing.pl",
        ]},
    )

    counts = result["counts"]
    # Only non-whitespace lines are counted.
    assert counts["data/level_1/objects.pl"] == 3
    assert counts["data/level_1/empty.pl"] == 0
    # Missing files are simply omitted.
    assert "data/level_1/missing.pl" not in counts


def test_line_counts_requires_list(tmp_path: Path, monkeypatch) -> None:
    workspace_id = _make_workspace(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        workspace_api.data_file_line_counts(workspace_id, {"paths": "not-a-list"})

    assert error.value.status_code == 400
