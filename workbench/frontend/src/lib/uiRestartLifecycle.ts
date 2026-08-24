import { useSyncExternalStore } from "react";

export type UiRestartReason = "server-restart" | "ui-reload" | "development-reload";

export type UiRestartContext = {
  token: string;
  reason: UiRestartReason;
  workspaceId: string;
  pageId: string;
  href: string;
  requestedAt: string;
};

type UiRestartHandler = (context: UiRestartContext) => void | Promise<void>;
type UiRestartGuard = UiRestartContext & {
  phase: "preparing" | "prepared" | "reloading" | "recovered" | "failed";
  reloadIssuedAt?: string;
  recoveredAt?: string;
  error?: string;
};

const UI_RESTART_GUARD_KEY = "metta-workbench.ui-restart-guard.v1";
export const ON_UI_RESTART_EVENT = "workbench:on-ui-restart";
export const UI_RESTART_STATUS_EVENT = "workbench:ui-restart-status";
const handlers = new Map<string, UiRestartHandler>();
let activeRestart: Promise<UiRestartContext> | null = null;
let cachedGuardSource: string | null | undefined;
let cachedGuard: UiRestartGuard | null = null;

const readGuard = (): UiRestartGuard | null => {
  try {
    const source = window.sessionStorage.getItem(UI_RESTART_GUARD_KEY);
    if (source !== cachedGuardSource) {
      cachedGuardSource = source;
      cachedGuard = source ? JSON.parse(source) as UiRestartGuard : null;
    }
    return cachedGuard;
  } catch {
    return null;
  }
};

const writeGuard = (guard: UiRestartGuard) => {
  const source = JSON.stringify(guard);
  window.sessionStorage.setItem(UI_RESTART_GUARD_KEY, source);
  cachedGuardSource = source;
  cachedGuard = guard;
  window.dispatchEvent(new CustomEvent(UI_RESTART_STATUS_EVENT, { detail: guard }));
};

export type UiRestartStatus = {
  pending: boolean;
  phase: UiRestartGuard["phase"] | "idle";
  reason?: UiRestartReason;
  requestedAt?: string;
};

let cachedStatusGuard: UiRestartGuard | null | undefined;
let cachedStatus: UiRestartStatus = { pending: false, phase: "idle" };

export function getUiRestartStatus(): UiRestartStatus {
  const guard = readGuard();
  if (guard === cachedStatusGuard) return cachedStatus;
  cachedStatusGuard = guard;
  cachedStatus = guard
    ? {
      pending: guard.phase === "preparing" || guard.phase === "prepared" || guard.phase === "reloading",
      phase: guard.phase,
      reason: guard.reason,
      requestedAt: guard.requestedAt,
    }
    : { pending: false, phase: "idle" };
  return cachedStatus;
}

function subscribeUiRestartStatus(listener: () => void): () => void {
  const onStorage = (event: StorageEvent) => {
    if (!event.key || event.key === UI_RESTART_GUARD_KEY) listener();
  };
  window.addEventListener(UI_RESTART_STATUS_EVENT, listener);
  window.addEventListener("storage", onStorage);
  return () => {
    window.removeEventListener(UI_RESTART_STATUS_EVENT, listener);
    window.removeEventListener("storage", onStorage);
  };
}

export function useUiRestartStatus(): UiRestartStatus {
  return useSyncExternalStore(subscribeUiRestartStatus, getUiRestartStatus, () => ({ pending: false, phase: "idle" }));
}

export function registerOnUIRestart(id: string, handler: UiRestartHandler): () => void {
  handlers.set(id, handler);
  return () => {
    if (handlers.get(id) === handler) handlers.delete(id);
  };
}

export function onUIRestart(input: Omit<UiRestartContext, "token" | "requestedAt">): Promise<UiRestartContext> {
  if (activeRestart) return activeRestart;
  activeRestart = (async () => {
    const context: UiRestartContext = {
      ...input,
      token: crypto.randomUUID(),
      requestedAt: new Date().toISOString(),
    };
    writeGuard({ ...context, phase: "preparing" });
    window.dispatchEvent(new CustomEvent(ON_UI_RESTART_EVENT, { detail: context }));
    const results = await Promise.allSettled([...handlers.values()].map(handler => handler(context)));
    const failures = results.filter(result => result.status === "rejected") as PromiseRejectedResult[];
    if (failures.length) {
      const error = failures.map(failure => String(failure.reason)).join("; ");
      writeGuard({ ...context, phase: "failed", error });
      throw new Error(`UI restart state flush failed: ${error}`);
    }
    writeGuard({ ...context, phase: "prepared" });
    return context;
  })().finally(() => {
    activeRestart = null;
  });
  return activeRestart;
}

export function permitUiReload(token: string): boolean {
  const guard = readGuard();
  if (!guard || guard.token !== token || guard.phase !== "prepared" || guard.reloadIssuedAt) return false;
  writeGuard({ ...guard, phase: "reloading", reloadIssuedAt: new Date().toISOString() });
  return true;
}

export function failUiRestart(token: string, reason: unknown): void {
  const guard = readGuard();
  if (!guard || guard.token !== token) return;
  writeGuard({ ...guard, phase: "failed", error: reason instanceof Error ? reason.message : String(reason) });
}

export function acknowledgeUiRestartRecovery(): UiRestartGuard | null {
  const guard = readGuard();
  if (!guard || guard.phase !== "reloading") return guard;
  const recovered = { ...guard, phase: "recovered" as const, recoveredAt: new Date().toISOString() };
  writeGuard(recovered);
  return recovered;
}
