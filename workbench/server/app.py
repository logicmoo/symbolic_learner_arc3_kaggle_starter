from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.workflow import router as workflow_router
from routes.artifacts import router as artifacts_router

app = FastAPI(title="MeTTaSymbolicLearnerWorkbench API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(workflow_router, prefix="/api")
app.include_router(artifacts_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "MeTTaSymbolicLearnerWorkbench"}
