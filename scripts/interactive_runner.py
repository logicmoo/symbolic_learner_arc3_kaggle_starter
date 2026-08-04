from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from llm_json_patch import install_llm_json_resilience

install_llm_json_resilience()

import interactive_runner as interactive_runner_ui
from llm_batch_profiles import install_batch_ui
from multillm_runner import install_interactive_runner

install_interactive_runner(interactive_runner_ui)
install_batch_ui(interactive_runner_ui)


if __name__ == "__main__":
    interactive_runner_ui.main()
