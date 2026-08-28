from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workbench" / "frontend" / "src" / "components" / "ChatConversation.tsx"
STYLES = ROOT / "workbench" / "frontend" / "src" / "styles" / "chat.css"


def test_chat_has_collapsible_schema_driven_mailbox_arranger() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")

    assert 'useState("server")' in source
    assert "showMailboxListSettings" in source
    assert 'aria-label="Mailbox list arrangement"' in source
    assert "Object.entries(option)" in source
    assert "groupFieldOptions.map" in source
    assert "cachedGroupFields" in source
    assert "mailboxDefinitionFields" in source
    assert "observation=mailbox_definition" in source
    assert "observation=chat_bubble" in source
    assert "mailbox=field_cache_config" in source
    assert "Field cache · mailbox definitions" in source
    assert '<option value="activity-minute">Activity · per minute</option>' in source
    assert '<option value="activity-hour">Activity · per hour</option>' in source
    assert '<option value="unread">Unread messages</option>' in source
    assert ".chat-mailbox-arranger" in styles


def test_chat_mailbox_counts_and_opening_use_personal_cursor() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert "/api/mailbox/mailboxes?agent=" in source
    assert "mailboxUnread.get(id)" in source
    assert "Numbers are messages past" in source
    assert '<option value="last-read">Resume at last read</option>' in source
    assert '<option value="end-mark-read">Go to end and mark read</option>' in source
    assert "lastReadMessageId" in source
    assert 'data-message-id={message.id}' in source
    assert 'void moveCursor("now", mailbox)' in source
    assert "Advance cursor when the end is viewed" in source
