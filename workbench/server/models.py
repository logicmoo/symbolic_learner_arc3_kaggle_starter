from typing import Any, Literal
from pydantic import BaseModel, Field


class ArcObject(BaseModel):
    id: str
    name: str
    color: int
    cells: list[tuple[int, int]]
    properties: dict[str, Any] = Field(default_factory=dict)
    turtle_program: str
    prolog_facts: str
    confidence: float


class RunStepResponse(BaseModel):
    session_id: str
    step_id: str
    status: Literal["completed", "failed"]
    logs: list[str]
    output_artifact_ids: list[str]
