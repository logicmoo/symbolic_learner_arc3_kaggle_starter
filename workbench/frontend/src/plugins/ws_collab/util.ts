import type { CollabEvent } from "./types";

export function shortTs(ts?: string): string {
  if (!ts) return "";
  const date = new Date(ts);
  if (Number.isNaN(date.getTime())) return ts;
  return date.toLocaleTimeString([], { hour12: false });
}

const TEXT_KEYS = ["text", "message", "content", "summary", "utterance"];

export function pickText(data: Record<string, unknown>): string {
  for (const key of TEXT_KEYS) {
    const value = data[key];
    if (typeof value === "string" && value.trim()) return value;
  }
  return "";
}

export function eventText(event: CollabEvent): string {
  return pickText(event.data ?? {});
}

export function compactData(event: CollabEvent): string {
  const serialized = JSON.stringify(event.data ?? {});
  return serialized.length > 160 ? `${serialized.slice(0, 157)}…` : serialized;
}
