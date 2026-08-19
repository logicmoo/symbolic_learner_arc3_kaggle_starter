from pathlib import Path

import prompt_api
from resource_store import get_filesystem_provider


def test_updates_only_selected_prompt_in_multi_resource_metta(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "project"
    path = root / "design" / "prompts" / "catalog.prompt.metta"
    resources = get_filesystem_provider()
    resources.write_json_resource(
        path,
        {"kind": "prompt", "id": "first", "label": "First", "text": ["old"]},
    )
    resources.write_json_resource(
        path,
        {"kind": "prompt", "id": "neighbor", "label": "Keep me", "text": ["same"]},
    )
    monkeypatch.setattr(
        prompt_api,
        "_resolve_workspace",
        lambda workspace_id: {"id": workspace_id, "root": str(root)},
    )

    result = prompt_api.update_prompt_resource(
        "project",
        "first",
        {
            "path": "design/prompts/catalog.prompt.metta",
            "document": {
                "kind": "prompt",
                "id": "first",
                "label": "First revised",
                "text": ["new"],
            },
        },
    )

    documents = resources.read_json_documents(path)
    assert result["document"]["label"] == "First revised"
    assert documents[0]["text"] == ["new"]
    assert documents[1] == {
        "kind": "prompt",
        "id": "neighbor",
        "label": "Keep me",
        "text": ["same"],
    }
