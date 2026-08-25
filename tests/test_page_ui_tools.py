from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "workbench" / "frontend" / "src"


def test_active_shell_places_shared_ui_tools_on_every_page():
    source = (FRONTEND / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert "<PageUiTools" in source
    assert "pageId={view}" in source
    assert 'onOpenChat={() => setView("chat")}' in source


def test_page_ui_tools_expose_options_and_contextual_codex_chat():
    source = (FRONTEND / "components" / "PageUiTools.tsx").read_text(encoding="utf-8")
    assert "Show UI Config Options Present" in source
    assert "Chat with Codex about this UI" in source
    assert "Current URL:" in source
    assert "symbolic-workbench" not in source  # routing identity stays in ChatPage


def test_page_session_state_is_keyed_by_workspace_and_page():
    source = (FRONTEND / "lib" / "pageSessionState.ts").read_text(encoding="utf-8")
    assert "window.sessionStorage" in source
    assert "encodeURIComponent(workspaceId)" in source
    assert "encodeURIComponent(pageId)" in source
    assert "scrollTop" in source
    assert "ui: Record<string, unknown>" in source


def test_ui_assistance_chat_uses_codex_and_prepared_draft():
    page = (FRONTEND / "components" / "ChatPage.tsx").read_text(encoding="utf-8")
    conversation = (FRONTEND / "components" / "ChatConversation.tsx").read_text(encoding="utf-8")
    assert '"symbolic-workbench-codex"' in page
    assert "UI_ASSISTANCE_CHAT_DRAFT_KEY" in page
    assert "initialInput={uiAssistanceDraft}" in page
    assert "initialInput?: string" in conversation


def test_chat_file_tab_embeds_super_control_and_selection_controls_source():
    page = (FRONTEND / "components" / "ChatPage.tsx").read_text(encoding="utf-8")
    conversation = (FRONTEND / "components" / "ChatConversation.tsx").read_text(encoding="utf-8")
    shell = (FRONTEND / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")

    assert 'import { SuperControl, type StandardSuperControlRequest }' in conversation
    assert '<SuperControl appearance="embedded" control={streamSuperControl}' in conversation
    assert 'aria-pressed={autoScroll}' in conversation
    assert "setAutoScrollEnabled(false)" in conversation
    assert "selectedMessageKey === bubbleKey(message)" in conversation
    assert "buildStreamFile(nextSelected)" in conversation
    assert 'kind: "chat_stream"' in conversation
    assert "records," in conversation
    assert "chat-filepane-text" not in conversation
    assert "workspaceId={workspaceId}" in page
    assert "<ChatPage workspaceId={workspace.id}" in shell


def test_chat_from_and_to_allow_explicit_null_endpoints():
    page = (FRONTEND / "components" / "ChatPage.tsx").read_text(encoding="utf-8")
    conversation = (FRONTEND / "components" / "ChatConversation.tsx").read_text(encoding="utf-8")

    assert 'inspectId("FROM", you)' in conversation
    assert ">From</button>" in conversation
    assert 'aria-label="From agent identity"' in conversation
    assert 'aria-label="To agent identity"' in conversation
    assert conversation.count('<option value="">(none/null)</option>') == 2
    assert '"(none/null)"' in conversation
    assert "!you || !target" in conversation
    assert "Select FROM and TO to send" in conversation
    assert "messages come FROM" in page


def test_surgical_ui_reloader_enters_restart_lifecycle():
    vite = (ROOT / "workbench" / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
    client = (FRONTEND / "lib" / "surgicalUiReloaderClient.ts").read_text(encoding="utf-8")
    assert 'event: "workbench:surgical-ui-change"' in vite
    assert 'type: "full-reload"' not in vite
    assert 'reason: "development-reload"' in client
    assert "await onUIRestart" in client
    assert "permitUiReload" in client


def test_restart_button_reports_pending_lifecycle_phase():
    shell = (FRONTEND / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    lifecycle = (FRONTEND / "lib" / "uiRestartLifecycle.ts").read_text(encoding="utf-8")
    assert "useUiRestartStatus" in shell
    assert "Saving UI state…" in shell
    assert "Restart pending…" in shell
    assert "Reloading UI…" in shell
    assert "UI_RESTART_STATUS_EVENT" in lifecycle
