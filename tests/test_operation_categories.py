import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_every_operation_has_at_least_one_valid_category_path() -> None:
    operations = list(WORKSPACES.glob("*/design/operations/*.operation.json"))
    assert operations
    for path in operations:
        document = json.loads(path.read_text(encoding="utf-8"))
        categories = document.get("categories")
        assert isinstance(categories, list) and categories, path
        assert all(isinstance(category, str) and category.strip(" /") for category in categories), path


def test_titlecase_llm_implementation_is_a_sample_llm() -> None:
    path = WORKSPACES / "shared" / "design" / "operation_implementations" / "echo_into_titlecased_llm.operation_implementation.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    assert "sample/llm" in document["categories"]
