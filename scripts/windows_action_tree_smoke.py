from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

from _runtime import configure_runtime_home


REPOSITORY_ROOT = configure_runtime_home(__file__)
PYTHON_ROOT = REPOSITORY_ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from action_tree import ActionTreeStore  # noqa: E402


def run_smoke(output_root: Path) -> dict[str, str]:
    output_root.mkdir(parents=True, exist_ok=True)
    store = ActionTreeStore(output_root, "windows_smoke", 1)
    node = store.create_initial(
        b"windows-smoke-image",
        {
            "state": "SMOKE_READY",
            "step_count": 0,
            "observation": {"source": "native_windows_smoke"},
        },
    )
    required = (node.state_path, node.image_path, node.readme_path)
    missing = tuple(str(path) for path in required if not path.is_file())
    if missing:
        raise RuntimeError(f"Windows smoke did not create required files: {missing}")
    metadata = store.metadata(node)
    if metadata.get("state") != "SMOKE_READY":
        raise RuntimeError("Windows smoke state did not round-trip")
    return {
        "repositoryRoot": str(REPOSITORY_ROOT),
        "pythonRoot": str(PYTHON_ROOT),
        "node": str(node.path),
        "state": str(node.state_path),
        "image": str(node.image_path),
        "readme": str(node.readme_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve native Windows launch paths and record one ARC3 action-tree node."
    )
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    if args.output_root is not None:
        result = run_smoke(args.output_root.resolve())
        print(json.dumps(result, sort_keys=True))
        return 0
    with tempfile.TemporaryDirectory(prefix="arc3_windows_smoke_") as directory:
        result = run_smoke(Path(directory))
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
