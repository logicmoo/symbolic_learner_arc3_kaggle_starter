from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from resource_store import get_filesystem_provider


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TODO_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "MODEL_RUNTIME_USAGE_AND_BENCHMARKING_POLICIES.md"
MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "model_runtime_policy_mockup.png"

router = APIRouter(prefix="/model-policy/todo", tags=["model-policy"])


@router.get("")
def get_model_policy_todo() -> dict[str, object]:
    resources = get_filesystem_provider()
    if not resources.is_file(TODO_PATH):
        raise HTTPException(status_code=404, detail="Model-policy TODO specification is missing")
    return {
        "status": "implemented-with-followups",
        "specificationPath": TODO_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupPath": MOCKUP_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupAvailable": resources.is_file(MOCKUP_PATH),
        "markdown": resources.read_text(TODO_PATH),
    }


@router.get("/mockup", response_class=Response)
def get_model_policy_mockup() -> Response:
    resources = get_filesystem_provider()
    if not resources.is_file(MOCKUP_PATH):
        raise HTTPException(status_code=404, detail="Model-policy mockup is missing")
    response = Response(resources.read_bytes(MOCKUP_PATH), media_type="image/png")
    response.path = MOCKUP_PATH
    return response
