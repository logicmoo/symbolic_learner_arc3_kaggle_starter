from __future__ import annotations

from _runtime import configure_runtime_home

PROJECT_ROOT = configure_runtime_home(__file__)

from interactive_runner import main


if __name__ == "__main__":
    main()
