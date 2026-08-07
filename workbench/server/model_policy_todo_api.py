from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TODO_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "MODEL_RUNTIME_USAGE_AND_BENCHMARKING_POLICIES.md"
MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "model_runtime_policy_mockup.png"

router = APIRouter(prefix="/model-policy/todo", tags=["model-policy"])


@router.get("")
def get_model_policy_todo() -> dict[str, object]:
    if not TODO_PATH.is_file():
        raise HTTPException(status_code=404, detail="Model-policy TODO specification is missing")
    return {
        "status": "pending",
        "specificationPath": TODO_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupPath": MOCKUP_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupAvailable": MOCKUP_PATH.is_file(),
        "markdown": TODO_PATH.read_text(encoding="utf-8"),
    }


@router.get("/mockup", response_class=FileResponse)
def get_model_policy_mockup() -> FileResponse:
    if not MOCKUP_PATH.is_file():
        raise HTTPException(status_code=404, detail="Model-policy mockup is missing")
    return FileResponse(MOCKUP_PATH, media_type="image/png", filename=MOCKUP_PATH.name)
