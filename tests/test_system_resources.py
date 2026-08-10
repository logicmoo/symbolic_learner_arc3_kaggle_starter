from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

from workspace_api import _load_systems  # noqa: E402


def test_shared_callable_systems_are_not_model_backends() -> None:
    shared = ROOT / "workbench" / "workspaces" / "shared"
    records = _load_systems({"id": "shared", "root": str(shared)})
    documents = {record["document"]["id"]: record["document"] for record in records}

    assert {"python", "prolog", "metta", "llm", "omegaclaw", "codex"} <= documents.keys()
    assert all(document["kind"] == "system" for document in documents.values())
    assert documents["llm"]["systemType"] == "llm_caller"
    assert not ({"openai", "anthropic", "openrouter", "groq"} & documents.keys())
