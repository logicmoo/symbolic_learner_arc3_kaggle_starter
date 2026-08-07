from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from model_policy_todo_api import get_model_policy_mockup, get_model_policy_todo  # noqa: E402


def test_model_policy_todo_is_read_from_checked_in_files() -> None:
    payload = get_model_policy_todo()
    assert payload["status"] == "pending"
    assert payload["mockupAvailable"] is True
    assert "Model Runtime Usage" in str(payload["markdown"])
    assert str(payload["specificationPath"]).endswith("MODEL_RUNTIME_USAGE_AND_BENCHMARKING_POLICIES.md")


def test_model_policy_mockup_endpoint_returns_checked_in_png() -> None:
    response = get_model_policy_mockup()
    assert response.media_type == "image/png"
    assert Path(response.path).is_file()


def test_active_model_policy_page_uses_filesystem_todo_api() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyTodoPage.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert 'fetch("/api/model-policy/todo")' in page
    assert "ReactMarkdown" in page
    assert 'src="/api/model-policy/todo/mockup"' in page
    assert 'view==="modelPolicy"&&<ModelPolicyTodoPage/>' in shell
