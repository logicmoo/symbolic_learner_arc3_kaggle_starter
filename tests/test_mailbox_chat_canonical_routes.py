from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAILBOX_SRC = ROOT / "workbench" / "plugins" / "mailbox_chat" / "src"
sys.path.insert(0, str(MAILBOX_SRC))

from mailbox_chat.ws_collab_api import handle_ws_collab_get  # noqa: E402


def test_mailbox_chat_exposes_unversioned_ws_collab_mailbox(tmp_path: Path) -> None:
    response = handle_ws_collab_get("/ws_collab/mailbox/agents", "", root=tmp_path)
    assert response is not None
    status, payload = response
    assert status == 200
    assert "agents" in payload
    assert all(agent.get("id") for agent in payload["agents"])


def test_workbench_manifests_publish_only_canonical_mailbox_paths() -> None:
    mailbox_manifest = json.loads(
        (ROOT / "workbench" / "plugins" / "mailbox_chat" / "plugin.json").read_text(encoding="utf-8")
    )
    ws_manifest = json.loads(
        (ROOT / "workbench" / "plugins" / "ws_collab" / "plugin.json").read_text(encoding="utf-8")
    )
    assert mailbox_manifest["mailboxEndpoint"]["path"] == "/ws_collab/mailbox/mailboxes"
    assert mailbox_manifest["mailboxEndpoint"]["websocket"] == "/ws_collab/ws"
    assert ws_manifest["plugin-init"][0]["redirect"].endswith("/ws_collab")
