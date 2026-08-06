from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["artifacts"])

ARTIFACTS = {
    "obj_blue_frame": {
        "id": "obj_blue_frame",
        "semantic_types": ["individual_object"],
        "data_types": ["image", "turtle_program", "prolog_facts"],
        "relationships": [
            "contained_by:scene-ls20-0-0",
            "derived_from:input-image-0001",
        ],
    },
    "obj_red_angle": {
        "id": "obj_red_angle",
        "semantic_types": ["individual_object"],
        "data_types": ["image", "turtle_program", "prolog_facts"],
        "relationships": [
            "contained_by:scene-ls20-0-0",
            "derived_from:input-image-0001",
        ],
    },
}


@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str) -> dict:
    if artifact_id not in ARTIFACTS:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ARTIFACTS[artifact_id]
