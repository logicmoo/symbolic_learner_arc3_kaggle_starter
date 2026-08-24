export type WorkbenchPageSessionState = {
  workspaceId: string;
  pageId: string;
  href: string;
  scrollTop: number;
  ui: Record<string, unknown>;
  lastUiRestartAt?: string;
  updatedAt: string;
};

const PREFIX = "metta-workbench.page-session.v1";

const keyFor = (workspaceId: string, pageId: string) =>
  `${PREFIX}:${encodeURIComponent(workspaceId)}:${encodeURIComponent(pageId)}`;

export function readWorkbenchPageSession(
  workspaceId: string,
  pageId: string,
): WorkbenchPageSessionState | null {
  try {
    const source = window.sessionStorage.getItem(keyFor(workspaceId, pageId));
    return source ? JSON.parse(source) as WorkbenchPageSessionState : null;
  } catch {
    return null;
  }
}

export function writeWorkbenchPageSession(
  workspaceId: string,
  pageId: string,
  patch: Partial<WorkbenchPageSessionState>,
): void {
  const previous = readWorkbenchPageSession(workspaceId, pageId);
  const next: WorkbenchPageSessionState = {
    workspaceId,
    pageId,
    href: window.location.href,
    scrollTop: 0,
    ui: {},
    ...previous,
    ...patch,
    updatedAt: new Date().toISOString(),
  };
  window.sessionStorage.setItem(keyFor(workspaceId, pageId), JSON.stringify(next));
}

export function markAllWorkbenchPageSessionsForRestart(restartedAt: string): void {
  for (let index = 0; index < window.sessionStorage.length; index += 1) {
    const key = window.sessionStorage.key(index);
    if (!key?.startsWith(`${PREFIX}:`)) continue;
    try {
      const state = JSON.parse(window.sessionStorage.getItem(key) || "") as WorkbenchPageSessionState;
      window.sessionStorage.setItem(key, JSON.stringify({ ...state, lastUiRestartAt: restartedAt, updatedAt: restartedAt }));
    } catch {
      // Preserve unrelated and malformed browser state; a page can rewrite its own entry later.
    }
  }
}

export const UI_ASSISTANCE_CHAT_DRAFT_KEY = "metta-workbench.ui-assistance-chat-draft.v1";
export const UI_ASSISTANCE_CHAT_DRAFT_EVENT = "workbench:ui-assistance-chat-draft";
