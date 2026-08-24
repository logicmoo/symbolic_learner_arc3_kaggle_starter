import { useState } from "react";
import { readWorkbenchPageSession, UI_ASSISTANCE_CHAT_DRAFT_EVENT, UI_ASSISTANCE_CHAT_DRAFT_KEY, writeWorkbenchPageSession } from "../lib/pageSessionState";
import { updateUserUiPreferences, useUserUiPreferences } from "../lib/uiPreferences";
import "../styles/page_ui_tools.css";

type Props = {
  pageId: string;
  pageLabel: string;
  workspaceId: string;
  onOpenChat: () => void;
};

export function PageUiTools({ pageId, pageLabel, workspaceId, onOpenChat }: Props) {
  const [optionsOpen, setOptionsOpenState] = useState(() => Boolean(readWorkbenchPageSession(workspaceId, pageId)?.ui.optionsOpen));
  const preferences = useUserUiPreferences();

  const openUiChat = () => {
    const prompt = [
      `Help me customize the ${pageLabel} page UI in MeTTaSymbolicLearnerWorkbench.`,
      `Workspace: ${workspaceId}`,
      `Page id: ${pageId}`,
      `Current URL: ${window.location.href}`,
      "First inspect the existing active page and its reusable components. Preserve rich editor behavior and real filesystem/backend data. Ask what I want changed, then help implement the UI safely.",
    ].join("\n");
    window.sessionStorage.setItem(UI_ASSISTANCE_CHAT_DRAFT_KEY, prompt);
    window.dispatchEvent(new CustomEvent(UI_ASSISTANCE_CHAT_DRAFT_EVENT, { detail: prompt }));
    onOpenChat();
  };

  const setOptionsOpen = (open: boolean) => {
    setOptionsOpenState(open);
    const previous = readWorkbenchPageSession(workspaceId, pageId);
    writeWorkbenchPageSession(workspaceId, pageId, { ui: { ...(previous?.ui || {}), optionsOpen: open } });
  };

  return <aside className="page-ui-tools" aria-label={`${pageLabel} page UI tools`}>
    <div className="page-ui-tools-actions">
      <span><b>{pageLabel}</b><small>Page state retained for this session</small></span>
      <button type="button" aria-expanded={optionsOpen} onClick={() => setOptionsOpen(!optionsOpen)}>
        {optionsOpen ? "Hide UI Config Options" : "Show UI Config Options Present"}
      </button>
      <button type="button" className="page-ui-codex-action" onClick={openUiChat}>Chat with Codex about this UI</button>
    </div>
    {optionsOpen && <div className="page-ui-options-present">
      <div><span>AVAILABLE USER/UI OPTION</span><b>Resource Source save/load placement</b><small>Shared by generic resource editors on this and other pages.</small></div>
      <label>PLACEMENT<select value={preferences.resourceSourceFileControlsPlacement} onChange={event => updateUserUiPreferences({resourceSourceFileControlsPlacement:event.target.value as "above"|"below"})}><option value="above">Above editor text</option><option value="below">Below editor text</option></select></label>
      <p>No page-specific options have been registered for <code>{pageId}</code> yet. New worthwhile UI choices should be registered in User/UI Settings and surfaced here.</p>
    </div>}
  </aside>;
}
