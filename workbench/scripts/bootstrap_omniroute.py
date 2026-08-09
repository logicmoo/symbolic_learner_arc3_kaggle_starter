from __future__ import annotations

import sys
from pathlib import Path


WORKBENCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKBENCH / "server"))

from backend_library import load_workspace_backend_records  # noqa: E402
from workspace_credentials import (  # noqa: E402
    bootstrap_backend_credential,
    resolve_workspace_credential,
)


def main() -> int:
    workspace_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else WORKBENCH / "workspaces" / "shared"
    if resolve_workspace_credential(workspace_root, "OMNIROUTE_API_KEY"):
        print("OmniRoute endpoint key is already configured.")
        return 0
    backend = next(
        (record.get("document") or record)
        for record in load_workspace_backend_records(workspace_root)
        if (record.get("document") or record).get("id") == "omniroute"
    )
    bootstrap_backend_credential(workspace_root, backend)
    print("OmniRoute endpoint key created and saved in the workspace credential store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
