// The admin bundle is served under `<mount>/admin/react/`, so the REST/WS mount
// is whatever precedes `/admin/react`. This keeps the client correct whether the
// server mounts ws_collab at `/ws_collab`, `/`, or anything else.
const match = location.pathname.match(/^(.*?)\/admin\/react(?:\/|$)/);
export const MOUNT = match ? match[1] : "/ws_collab";
export const REST = `${MOUNT}/v1`;

export async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${REST}${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

export function wsUrl(): string {
  const scheme = location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${location.host}${MOUNT}/ws`;
}
