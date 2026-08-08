from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_every_operation_has_at_least_one_valid_category_path() -> None:
    resources = get_filesystem_provider()
    operations = list(WORKSPACES.glob("*/design/operations/*.operation.metta"))
    assert operations
    for path in operations:
        document = resources.read_json(path.with_suffix(".json"))
        categories = document.get("categories")
        assert isinstance(categories, list) and categories, path
        assert all(isinstance(category, str) and category.strip(" /") for category in categories), path


def test_titlecase_llm_implementation_is_a_sample_llm() -> None:
    path = WORKSPACES / "shared" / "design" / "operations" / "echo_into_titlecased_llm.operation.json"
    document = get_filesystem_provider().read_json(path)
    assert document["kind"] == "operation"
    assert document["parents"] == ["echo_into_titlecased"]
    assert "sample/llm" in document["categories"]
