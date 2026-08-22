"""Standalone FastAPI app for llm_emul.api.

Exposes the SAME router that's normally mounted inside the main
workbench server (workbench/server/app.py, on port 8000) -- but as its
own app, so it can be run on a separate port independent of the rest of
the workbench. See workbench/scripts/run_llm_emul_standalone.py for the
runnable entrypoint.
"""
from __future__ import annotations

from fastapi import FastAPI

from llm_emul.api import router as llm_emul_router

app = FastAPI(title="llm_emul (standalone)")
app.include_router(llm_emul_router)
