// Dev-only stylesheet auto-refresh, driven entirely by the page (no Vite HMR).
//
// The running app polls every already-loaded CSS module off disk on an interval
// and swaps it into the page when the bytes change. It works by asking the Vite
// dev server for each stylesheet's compiled text via the `?direct` endpoint
// (which recompiles from disk on every request) and writing that text back into
// the very <style> element Vite injected for that module. Nothing here depends
// on the HMR websocket, so it keeps working with `server.hmr` disabled.

const POLL_MS = 1000;

type Tracked = { url: string; el: HTMLStyleElement; last: string | null };

// Collect the <style> tags Vite injected for real CSS imports. Each carries a
// `data-vite-dev-id` absolute path; we map it to the browser-served `/src/...`
// URL. Only already-injected stylesheets are tracked, so we never load a CSS
// file the app did not import.
function collectTracked(previous: Tracked[]): Tracked[] {
  const lastByUrl = new Map(previous.map((entry) => [entry.url, entry.last]));
  const out: Tracked[] = [];
  const seen = new Set<string>();
  document.querySelectorAll<HTMLStyleElement>("style[data-vite-dev-id]").forEach((el) => {
    const id = (el.getAttribute("data-vite-dev-id") || "").replaceAll("\\", "/");
    if (!id.endsWith(".css")) return;
    const idx = id.indexOf("/src/");
    if (idx < 0) return;
    const url = id.slice(idx);
    if (seen.has(url)) return;
    seen.add(url);
    out.push({ url, el, last: lastByUrl.get(url) ?? null });
  });
  return out;
}

export function startCssHotPoll(): void {
  if (!import.meta.env.DEV) return;
  const flag = window as unknown as { __cssHotPoll?: boolean };
  if (flag.__cssHotPoll) return;
  flag.__cssHotPoll = true;

  let tracked: Tracked[] = collectTracked([]);
  let busy = false;

  const tick = async () => {
    if (busy) return;
    busy = true;
    try {
      tracked = collectTracked(tracked);
      await Promise.all(
        tracked.map(async (entry) => {
          try {
            const res = await fetch(`${entry.url}?direct&t=${Date.now()}`, { cache: "no-store" });
            if (!res.ok) return;
            const text = await res.text();
            if (entry.last === null) {
              entry.last = text; // prime without touching the DOM
              return;
            }
            if (text !== entry.last) {
              entry.el.textContent = text;
              entry.last = text;
              console.info(`[css-poll] reloaded ${entry.url}`);
            }
          } catch {
            // Transient dev-server hiccup; retry on the next tick.
          }
        }),
      );
    } finally {
      busy = false;
    }
  };

  window.setInterval(() => { void tick(); }, POLL_MS);
  console.info("[css-poll] polling app stylesheets off disk every " + POLL_MS + "ms (dev only)");
}
