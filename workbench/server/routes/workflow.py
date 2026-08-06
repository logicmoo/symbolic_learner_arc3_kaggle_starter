from fastapi import APIRouter
from models import RunStepResponse

router = APIRouter(tags=["workflow"])


@router.post(
    "/sessions/{session_id}/steps/{step_id}/run",
    response_model=RunStepResponse,
)
def run_step(session_id: str, step_id: str) -> RunStepResponse:
    return RunStepResponse(
        session_id=session_id,
        step_id=step_id,
        status="completed",
        logs=[
            f"Starting {step_id}",
            "Resolved input artifacts",
            "Generated semantic output bundle",
            "Stage completed",
        ],
        output_artifact_ids=[f"artifact-{step_id}-001"],
    )


@router.post("/sessions/{session_id}/reset")
def reset_session(session_id: str) -> dict[str, str]:
    return {"session_id": session_id, "status": "reset"}
