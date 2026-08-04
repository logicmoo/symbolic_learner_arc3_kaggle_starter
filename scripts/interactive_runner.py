from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from llm_json_patch import install_llm_json_resilience

install_llm_json_resilience()

import interactive_runner as interactive_runner_ui
from llm_catalog_environment import install_profile_environment
from llm_catalog_integration import install_catalog_runner
from llm_profile_editor import install_profile_editor_ui
from llm_workflows import install_workflow_router, install_workflow_ui
from multillm_runner import install_interactive_runner

install_profile_environment()
install_catalog_runner()
install_workflow_router()
install_interactive_runner(interactive_runner_ui)
install_profile_editor_ui(interactive_runner_ui)
install_workflow_ui(interactive_runner_ui)


if __name__ == "__main__":
    interactive_runner_ui.main()
