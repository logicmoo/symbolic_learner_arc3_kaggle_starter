from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from llm_json_patch import install_llm_json_resilience

install_llm_json_resilience()

import interactive_runner as interactive_runner_ui
from llm_catalog_environment import install_profile_environment
from llm_catalog_integration import install_catalog_runner
from llm_key_controls import install_llm_key_controls
from llm_profile_editor import install_profile_editor_ui
from llm_workflow_editor import install_workflow_editor_ui
from llm_workflows import install_workflow_router
from multillm_runner import install_interactive_runner
from workflow_task_editor import install_workflow_task_editor_ui
from workflow_tasks import install_task_workflows

install_profile_environment()
install_catalog_runner()
install_workflow_router()
install_task_workflows()
install_interactive_runner(interactive_runner_ui)
install_profile_editor_ui(interactive_runner_ui)
# Install the typed editor first. It consumes uppercase W and returns Enter, so
# the legacy workflow wrapper remains available for compatibility/help without
# intercepting W before the typed task/slot editor.
install_workflow_task_editor_ui(interactive_runner_ui)
install_workflow_editor_ui(interactive_runner_ui)
install_llm_key_controls(interactive_runner_ui)


if __name__ == "__main__":
    interactive_runner_ui.main()
