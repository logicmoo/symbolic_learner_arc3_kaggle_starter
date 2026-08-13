from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_every_operation_has_at_least_one_valid_category_path() -> None:
    resources = get_filesystem_provider()
    operations = list(WORKSPACES.glob("*/design/operations/*.operation.metta"))
    assert operations
    for path in operations:
        payload = resources.read_json(path.with_suffix(".json"))
        documents = payload if isinstance(payload, list) else [payload]
        for document in documents:
            categories = document.get("categories")
            assert isinstance(categories, list) and categories, (path, document.get("id"))
            assert all(isinstance(category, str) and category.strip(" /") for category in categories), (path, document.get("id"))


def test_titlecase_llm_implementation_is_a_sample_llm() -> None:
    path = WORKSPACES / "shared_library_system" / "design" / "operations" / "echo_into_titlecased_llm.operation.metta"
    document = get_filesystem_provider().read_json(path)
    assert document["kind"] == "operation"
    assert document["parents"] == ["echo_into_titlecased"]
    assert "sample/llm" in document["categories"]
