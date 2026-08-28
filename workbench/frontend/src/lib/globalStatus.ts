import { useSyncExternalStore } from "react";

/**
 * The global status feed: any page or tool can push a line, and the
 * app-wide status footer shows the latest (with the recent trail on hover).
 */
export type GlobalStatusEntry = { at: string; source: string; text: string };

const MAX_ENTRIES = 30;
let entries: GlobalStatusEntry[] = [];
const listeners = new Set<() => void>();

export function pushGlobalStatus(text: string, source = "app"): void {
  const at = new Date().toLocaleTimeString([], { hour12: false });
  entries = [...entries.slice(-(MAX_ENTRIES - 1)), { at, source, text }];
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

const EMPTY: GlobalStatusEntry[] = [];

export function useGlobalStatus(): GlobalStatusEntry[] {
  return useSyncExternalStore(subscribe, () => entries, () => EMPTY);
}
