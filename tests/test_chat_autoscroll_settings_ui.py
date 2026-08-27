from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workbench" / "frontend" / "src" / "components" / "ChatConversation.tsx"
STYLES = ROOT / "workbench" / "frontend" / "src" / "styles" / "chat.css"


def test_chat_autoscroll_supports_global_policy_and_stream_override() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert 'type AutoScrollPolicy = "always-on" | "allow-off"' in source
    assert "autoScrollByMailbox" in source
    assert "autoScrollDefault" in source
    assert "autoScrollPolicy" in source
    assert "Use ${mailboxLabel(mailbox)} Setting" in source
    assert '<option value="always-on">Always on</option>' in source
    assert '<option value="allow-off">Allow off</option>' in source
    assert 'disabled={autoScrollPolicy === "always-on"}' in source


def test_chat_controls_follow_requested_visible_line_order() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")

    expected_orders = {
        ".chat-require-summary": -10,
        ".chat-make": 10,
        ".chat-sub": 20,
        ".chat-address-from-to": 30,
        ".chat-address-send": 40,
        ".chat-stream-configuration": 50,
        ".chat-controls-divider": 60,
        ".chat-control--tabs": 70,
        ".chat-mailbox-add": 80,
        ".chat-mailbox-primary": 80,
        ".chat-mailbox-merged": 90,
    }
    for selector, order in expected_orders.items():
        start = styles.index(f"\n{selector} {{")
        end = styles.index("}", start)
        assert f"order: {order};" in styles[start:end]

    assert "showRequireMatchSettings" in source
    assert "is-match-collapsed" in source
    assert "chat-match-detail" in source
    assert ".chat-controls.is-match-collapsed .chat-match-detail" in styles
    assert "chat-require-summary-toggle" in source
    assert "Stream configuration panel for ${mailboxLabel(mailbox)}" in source
    assert ".chat-mbrow.chat-mailbox-primary" in styles
    assert ".chat-mbrow.chat-mailbox-add" in styles


def test_mailbox_config_is_a_tab_beside_file_not_a_bottom_panel() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert 'useState<"chat" | "file" | "config">("chat")' in source
    assert source.count('setPaneTab("config")}>Config</button>') == 2
    assert 'paneTab === "config"' in source
    assert 'role="tabpanel" aria-label="Mailbox configuration"' in source
    assert source.index('paneTab === "config"') < source.index('className="chat-composer"')
