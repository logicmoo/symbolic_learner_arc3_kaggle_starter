import { useEffect } from "react";

export const PAGE_PROCESS_ACTIVITY_EVENT = "workbench:process-activity";
export const RESTART_PENDING_CHANGE_EVENT = "workbench:restart-pending-change";
export const RESTART_PENDING_REQUEST_EVENT = "workbench:restart-pending-request";
export const RESTART_PENDING_CLEARED_EVENT = "workbench:restart-pending-cleared";
export const WORKBENCH_PRESENCE_EVENT = "workbench:presence";
const GLOBAL_FRAME_CHANNEL = "workbench-global-frame-v1";
const WORKBENCH_TAB_ID = crypto.randomUUID();

export type PageProcessActivity = {
  id: string;
  active: boolean;
  label: string;
};

export type RestartPendingRequest = {
  reason: string;
  changes?: string[];
};

export type WorkbenchPresence = {
  tabId: string;
  workspaceId: string;
  pageId: string;
  href: string;
  active: boolean;
  seenAt: number;
};

type GlobalFrameMessage =
  | { event: typeof PAGE_PROCESS_ACTIVITY_EVENT; detail: PageProcessActivity }
  | { event: typeof RESTART_PENDING_CHANGE_EVENT; detail: string }
  | { event: typeof RESTART_PENDING_REQUEST_EVENT; detail: RestartPendingRequest }
  | { event: typeof RESTART_PENDING_CLEARED_EVENT; detail: { reason: string } }
  | { event: typeof WORKBENCH_PRESENCE_EVENT; detail: WorkbenchPresence };

const globalFrameChannel = typeof BroadcastChannel === "undefined" ? null : new BroadcastChannel(GLOBAL_FRAME_CHANNEL);
if (globalFrameChannel) {
  globalFrameChannel.onmessage = (message: MessageEvent<GlobalFrameMessage>) => {
    const payload = message.data;
    if (!payload?.event) return;
    window.dispatchEvent(new CustomEvent(payload.event, { detail: payload.detail }));
  };
}

function publishGlobalFrameMessage(message: GlobalFrameMessage): void {
  window.dispatchEvent(new CustomEvent(message.event, { detail: message.detail }));
  globalFrameChannel?.postMessage(message);
}

export function reportPageProcessActivity(activity: PageProcessActivity): void {
  publishGlobalFrameMessage({ event: PAGE_PROCESS_ACTIVITY_EVENT, detail: activity });
}

export function reportRestartPendingChange(change: string): void {
  publishGlobalFrameMessage({ event: RESTART_PENDING_CHANGE_EVENT, detail: change });
}

export function requestRestartPending(request: RestartPendingRequest): void {
  publishGlobalFrameMessage({ event: RESTART_PENDING_REQUEST_EVENT, detail: request });
  void fetch("/workbench/system/restart-pending", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ active: true, ...request }),
    keepalive: true,
  }).catch(() => undefined);
}

export function clearRestartPending(reason: string): void {
  publishGlobalFrameMessage({ event: RESTART_PENDING_CLEARED_EVENT, detail: { reason } });
  void fetch("/workbench/system/restart-pending", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ active: false, reason }),
    keepalive: true,
  }).catch(() => undefined);
}

export function reportWorkbenchPresence(presence: WorkbenchPresence): void {
  publishGlobalFrameMessage({ event: WORKBENCH_PRESENCE_EVENT, detail: presence });
  void fetch("/workbench/system/presence", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(presence),
    keepalive: true,
  }).catch(() => undefined);
}

export function useWorkbenchPresence(workspaceId: string, pageId: string): void {
  useEffect(() => {
    const report = (active: boolean) => reportWorkbenchPresence({
      tabId: WORKBENCH_TAB_ID,
      workspaceId,
      pageId,
      href: window.location.href,
      active,
      seenAt: Date.now(),
    });
    report(true);
    const timer = window.setInterval(() => report(true), 5000);
    const onVisible = () => report(true);
    window.addEventListener("pageshow", onVisible);
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("pageshow", onVisible);
      document.removeEventListener("visibilitychange", onVisible);
      report(false);
    };
  }, [pageId, workspaceId]);
}

export function usePageProcessActivity(id: string, active: boolean, label: string): void {
  useEffect(() => {
    reportPageProcessActivity({ id: `${WORKBENCH_TAB_ID}:${id}`, active, label });
  }, [active, id, label]);
  useEffect(() => () => {
    reportPageProcessActivity({ id: `${WORKBENCH_TAB_ID}:${id}`, active: false, label });
  }, [id, label]);
}
