from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

import interactive_runner as interactive_runner_ui
from multillm_runner import install_interactive_runner

install_interactive_runner(interactive_runner_ui)


if __name__ == "__main__":
    interactive_runner_ui.main()
