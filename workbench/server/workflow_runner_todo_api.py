from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TODO_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "WORKFLOW_RUNNER_EXPERIENCE.md"
MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_mockup.png"
CHRONOLOGY_MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_chronology_mockup.png"
HUMAN_INPUT_MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_human_input_mockup.png"

router = APIRouter(prefix="/workflow-runner/todo", tags=["workflow-runner"])


@router.get("")
def get_workflow_runner_todo() -> dict[str, object]:
    if not TODO_PATH.is_file():
        raise HTTPException(status_code=404, detail="Workflow-runner TODO specification is missing")
    return {
        "status": "design-reference",
        "specificationPath": TODO_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupPath": MOCKUP_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupAvailable": MOCKUP_PATH.is_file(),
        "mockups": [
            {"view": "Topology", "description": "Dependency and branch structure", "available": MOCKUP_PATH.is_file(), "url": "/api/workflow-runner/todo/mockup"},
            {"view": "Chronology", "description": "Persisted execution order and repeated stages", "available": CHRONOLOGY_MOCKUP_PATH.is_file(), "url": "/api/workflow-runner/todo/mockup/chronology"},
            {"view": "Human Input", "description": "Suspended execution and user-input context", "available": HUMAN_INPUT_MOCKUP_PATH.is_file(), "url": "/api/workflow-runner/todo/mockup/human-input"},
        ],
        "markdown": TODO_PATH.read_text(encoding="utf-8"),
    }


@router.get("/mockup", response_class=FileResponse)
def get_workflow_runner_mockup() -> FileResponse:
    if not MOCKUP_PATH.is_file():
        raise HTTPException(status_code=404, detail="Workflow-runner mockup is missing")
    return FileResponse(MOCKUP_PATH, media_type="image/png", filename=MOCKUP_PATH.name)


@router.get("/mockup/chronology", response_class=FileResponse)
def get_workflow_runner_chronology_mockup() -> FileResponse:
    if not CHRONOLOGY_MOCKUP_PATH.is_file():
        raise HTTPException(status_code=404, detail="Workflow-runner chronology mockup is missing")
    return FileResponse(CHRONOLOGY_MOCKUP_PATH, media_type="image/png", filename=CHRONOLOGY_MOCKUP_PATH.name)


@router.get("/mockup/human-input", response_class=FileResponse)
def get_workflow_runner_human_input_mockup() -> FileResponse:
    if not HUMAN_INPUT_MOCKUP_PATH.is_file():
        raise HTTPException(status_code=404, detail="Workflow-runner human-input mockup is missing")
    return FileResponse(HUMAN_INPUT_MOCKUP_PATH, media_type="image/png", filename=HUMAN_INPUT_MOCKUP_PATH.name)
