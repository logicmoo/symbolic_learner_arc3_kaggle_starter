from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/repository", tags=["repository-docs"])
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@router.get("/markdown")
def read_repository_markdown(path: str = Query(..., min_length=1)) -> dict[str, str]:
    target = (REPOSITORY_ROOT / path).resolve()
    try:
        target.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Markdown path must stay inside the repository") from error
    if target.suffix.lower() != ".md":
        raise HTTPException(status_code=400, detail="Only Markdown documents can be read")
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"Markdown document not found: {path}")
    return {"path": target.relative_to(REPOSITORY_ROOT).as_posix(), "content": target.read_text(encoding="utf-8")}
