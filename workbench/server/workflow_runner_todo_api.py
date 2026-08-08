from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from resource_store import get_filesystem_provider

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TODO_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "WORKFLOW_RUNNER_EXPERIENCE.md"
MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_mockup.png"
CHRONOLOGY_MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_chronology_mockup.png"
HUMAN_INPUT_MOCKUP_PATH = REPOSITORY_ROOT / "workbench" / "docs" / "todo" / "assets" / "workflow_runner_human_input_mockup.png"

router = APIRouter(prefix="/workflow-runner/todo", tags=["workflow-runner"])


@router.get("")
def get_workflow_runner_todo() -> dict[str, object]:
    resources = get_filesystem_provider()
    if not resources.is_file(TODO_PATH):
        raise HTTPException(status_code=404, detail="Workflow-runner TODO specification is missing")
    return {
        "status": "design-reference",
        "specificationPath": TODO_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupPath": MOCKUP_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
        "mockupAvailable": resources.is_file(MOCKUP_PATH),
        "mockups": [
            {"view": "Topology", "description": "Dependency and branch structure", "available": resources.is_file(MOCKUP_PATH), "url": "/api/workflow-runner/todo/mockup"},
            {"view": "Chronology", "description": "Persisted execution order and repeated stages", "available": resources.is_file(CHRONOLOGY_MOCKUP_PATH), "url": "/api/workflow-runner/todo/mockup/chronology"},
            {"view": "Human Input", "description": "Suspended execution and user-input context", "available": resources.is_file(HUMAN_INPUT_MOCKUP_PATH), "url": "/api/workflow-runner/todo/mockup/human-input"},
        ],
        "markdown": resources.read_text(TODO_PATH),
    }


@router.get("/mockup", response_class=Response)
def get_workflow_runner_mockup() -> Response:
    resources = get_filesystem_provider()
    if not resources.is_file(MOCKUP_PATH):
        raise HTTPException(status_code=404, detail="Workflow-runner mockup is missing")
    response = Response(resources.read_bytes(MOCKUP_PATH), media_type="image/png")
    response.path = MOCKUP_PATH
    return response


@router.get("/mockup/chronology", response_class=Response)
def get_workflow_runner_chronology_mockup() -> Response:
    resources = get_filesystem_provider()
    if not resources.is_file(CHRONOLOGY_MOCKUP_PATH):
        raise HTTPException(status_code=404, detail="Workflow-runner chronology mockup is missing")
    response = Response(resources.read_bytes(CHRONOLOGY_MOCKUP_PATH), media_type="image/png")
    response.path = CHRONOLOGY_MOCKUP_PATH
    return response


@router.get("/mockup/human-input", response_class=Response)
def get_workflow_runner_human_input_mockup() -> Response:
    resources = get_filesystem_provider()
    if not resources.is_file(HUMAN_INPUT_MOCKUP_PATH):
        raise HTTPException(status_code=404, detail="Workflow-runner human-input mockup is missing")
    response = Response(resources.read_bytes(HUMAN_INPUT_MOCKUP_PATH), media_type="image/png")
    response.path = HUMAN_INPUT_MOCKUP_PATH
    return response
