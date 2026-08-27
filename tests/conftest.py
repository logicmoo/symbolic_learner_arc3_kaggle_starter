"""Suite-wide safety defaults for Workbench plugin integration tests."""

from __future__ import annotations

import os
import uuid


# Importing the real Workbench app starts every startup plugin. Keep the task
# harness recovery scan and TestClient shutdown hooks away from operator-owned
# durable tasks even when a test imports ``workbench/server/app.py`` directly.
os.environ["LLM_TASK_HARNESS_STATE_DIRECTORY"] = (
    f".codex/pytest-llm-task-harness-runtime-{os.getpid()}-{uuid.uuid4().hex}"
)
