import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Recognition Demos — runs the symbolic_arc Phase-2 acceptance behaviours
 * (SOW Exhibit A Phase 2) as visual, re-runnable cards: occlusion completion,
 * recolour / resize identity, store-then-recognize, regeneration, replay, and
 * input breadth (raster / simple video). Data comes from the real recognizer via
 * GET /workbench/recognition/demos — no mocks.
 */

type Cell = { x: number; y: number; role: string; color: string | null };
type Panel = { label: string; w: number; h: number; cells: Cell[]; aux?: Panel };
type Demo = {
  id: string; group: string; title: string; description: string;
  panels: Panel[]; frames?: Panel[]; result: Record<string, unknown>; passed: boolean;
  notRun?: boolean; preview?: Panel | null; resultKeys?: string[];
  frameIndex?: number; playing?: boolean;
};
type CatalogEntry = { id: string; group: string; title: string; preview?: Panel | null; resultKeys?: string[] };
type CoverageRow = {
  phase: string; id: string; title: string;
  implemented: "full" | "partial" | "none"; llmFree: "full" | "partial" | "none";
  demo: string | null; demoStatus: "demo" | "no-demo" | "not-done";
};
type Ls20Recording = { key: string; label: string; count: number };
type DemosResponse = {
  demos: Demo[]; total: number; passed: number; running?: boolean; catalog?: CatalogEntry[];
  coverage?: CoverageRow[]; only?: string | null; anyPlaying?: boolean; playEpoch?: number;
  ls20Recordings?: Ls20Recording[]; ls20Source?: string | null; ls20StoreMode?: string;
};

const CELL = 16;
const MAX_PX = 360;

function GridPanel({ panel, reserveW, reserveH }: { panel: Panel; reserveW?: number; reserveH?: number }) {
  const px = Math.max(3, Math.min(CELL, Math.floor(MAX_PX / Math.max(panel.w, panel.h, 1))));
  const W = panel.w * px;
  const H = panel.h * px;
  const boxW = Math.max(reserveW || 0, W);
  const boxH = Math.max(reserveH || 0, H);
  const dense = Math.max(panel.w, panel.h) >= 24;  // big real scenes: draw as a clean bitmap
  return (
    <figure style={{ margin: 0, display: "flex", flexDirection: "column", gap: 4, alignItems: "center" }}>
      {/* Reserve a fixed box (max over all frames) so switching frames of different
          sizes does not resize the card and shove the whole grid around. */}
      <div style={{ width: boxW, height: boxH, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} shapeRendering="crispEdges"
        style={{ background: "#0b0f1a", borderRadius: 4, border: "1px solid #1c2333" }}>
        {panel.cells.map((c, i) => {
          const x = c.x * px;
          const y = c.y * px;
          if (c.role === "hidden") {
            return (
              <g key={i}>
                <rect x={x} y={y} width={px} height={px} fill="#161b26" stroke="#2a3346" />
                <rect x={x + 0.5} y={y + 0.5} width={px - 1} height={px - 1} fill="none"
                  stroke="#7c8598" strokeWidth={1} strokeDasharray="2 2" />
                {px >= 10 ? <text x={x + px / 2} y={y + px / 2 + 3} fontSize={px * 0.6}
                  textAnchor="middle" fill="#7c8598">?</text> : null}
              </g>
            );
          }
          const fill = c.color || "#8a8f98";
          const filled = c.role === "filled";
          const regen = c.role === "regen";
          // Dense real scenes: draw every cell as a borderless bitmap pixel so the
          // scene renders faithfully and grid lines don't swamp the image.
          if (dense && !filled && c.role !== "hidden") {
            return <rect key={i} x={x} y={y} width={px} height={px} fill={fill} />;
          }
          return (
            <g key={i}>
              <rect x={x + 0.5} y={y + 0.5} width={px - 1} height={px - 1} fill={fill}
                stroke={filled ? "#8bd450" : regen ? "#8bd450" : "rgba(0,0,0,0.35)"}
                strokeWidth={filled || regen ? 1.5 : 1} opacity={regen ? 0.85 : 1} />
              {filled && px >= 10 ? <text x={x + px / 2} y={y + px / 2 + 3} fontSize={px * 0.6}
                textAnchor="middle" fill="#0b0f1a" fontWeight={700}>+</text> : null}
            </g>
          );
        })}
      </svg>
      </div>
      <figcaption style={{
        fontSize: 10.5, opacity: 0.7, textAlign: "center", maxWidth: boxW + 40,
        height: 28, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2,
        WebkitBoxOrient: "vertical", lineHeight: "14px",
      }}>{panel.label}</figcaption>
    </figure>
  );
}

function BlankMap({ n = 12 }: { n?: number }) {
  const px = 14;
  const W = n * px;
  return (
    <figure style={{ margin: 0, display: "flex", flexDirection: "column", gap: 4, alignItems: "center" }}>
      <svg width={W} height={W} viewBox={`0 0 ${W} ${W}`}
        style={{ background: "#0b0f1a", borderRadius: 4, border: "1px solid #1c2333" }}>
        {Array.from({ length: n }).map((_, r) =>
          Array.from({ length: n }).map((__, c) => (
            <rect key={`${r}-${c}`} x={c * px + 0.5} y={r * px + 0.5} width={px - 1} height={px - 1}
              fill="none" stroke="#141a27" strokeWidth={1} />
          )),
        )}
      </svg>
      <figcaption style={{ fontSize: 10.5, opacity: 0.5, textAlign: "center" }}>blank map — nothing recognized yet</figcaption>
    </figure>
  );
}

function PreRunControls({ onRun, onStep, disabled }: { onRun: () => void; onStep: () => void; disabled: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
      <button type="button" disabled title="Previous step"
        style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "not-allowed", opacity: 0.4 }}>◀</button>
      <button type="button" disabled={disabled} title="Run &amp; play" onClick={onRun}
        style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: disabled ? "not-allowed" : "pointer" }}>▶</button>
      <button type="button" disabled={disabled} title="Run step 1 (start paused, then step)" onClick={onStep}
        style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: disabled ? "not-allowed" : "pointer" }}>▶❙</button>
      <input type="range" min={0} max={0} value={0} disabled readOnly style={{ width: 110, opacity: 0.4 }} />
      <span style={{ opacity: 0.5, minWidth: 42, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>step 1</span>
    </div>
  );
}

function ResultChips({ result }: { result: Record<string, unknown> }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
      {Object.entries(result).map(([k, v]) => (
        <span key={k} style={{
          fontSize: 11, padding: "2px 7px", borderRadius: 5, background: "rgba(255,255,255,0.05)",
          border: "1px solid rgba(255,255,255,0.08)",
        }}>
          <span style={{ opacity: 0.6 }}>{k}:</span>{" "}
          <b>{Array.isArray(v) ? v.join(", ") : v === null ? "—" : String(v)}</b>
        </span>
      ))}
    </div>
  );
}

function AnimatedGrid({ frames, index = 0, playing = false, onToggle, onSeek }: {
  frames: Panel[]; index?: number; playing?: boolean;
  onToggle?: (playing: boolean) => void; onSeek?: (index: number) => void;
}) {
  const multi = frames.length > 1;
  if (!frames.length) return <div style={{ opacity: 0.5, fontSize: 12 }}>no frames</div>;
  // The SERVER owns the playhead: render exactly the frame index it reports. No
  // client-side timer advances frames — the demo just displays what it's told.
  const i = Math.max(0, Math.min(index, frames.length - 1));
  const cur = frames[i];
  // Reserve the largest rendered box across ALL frames so frames of different sizes
  // don't resize the card mid-animation (which shoves the rest of the grid around).
  const pxOf = (p: Panel) => Math.max(3, Math.min(CELL, Math.floor(MAX_PX / Math.max(p.w, p.h, 1))));
  const dimW = (p: Panel) => p.w * pxOf(p);
  const dimH = (p: Panel) => p.h * pxOf(p);
  const maxMainW = Math.max(...frames.map(dimW));
  const maxMainH = Math.max(...frames.map(dimH));
  const auxFrames = frames.filter((f) => f.aux) as (Panel & { aux: Panel })[];
  const maxAuxW = auxFrames.length ? Math.max(...auxFrames.map((f) => dimW(f.aux))) : 0;
  const maxAuxH = auxFrames.length ? Math.max(...auxFrames.map((f) => dimH(f.aux))) : 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "center" }}>
      <div style={{ display: "flex", gap: 10, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "center" }}>
        <GridPanel panel={cur} reserveW={maxMainW} reserveH={maxMainH} />
        {cur.aux ? <GridPanel panel={cur.aux} reserveW={maxAuxW} reserveH={maxAuxH} /> : null}
      </div>
      {multi ? (
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
          <button type="button" title="Previous step"
            onClick={() => onSeek?.((i - 1 + frames.length) % frames.length)}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>◀</button>
          <button type="button" title={playing ? "Pause" : "Play"}
            onClick={() => onToggle?.(!playing)}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>{playing ? "⏸" : "▶"}</button>
          <button type="button" title="Next step"
            onClick={() => onSeek?.((i + 1) % frames.length)}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>▶❙</button>
          <input type="range" min={0} max={frames.length - 1} value={i}
            onChange={(e) => onSeek?.(Number(e.target.value))} style={{ width: 110 }} />
          <span style={{ opacity: 0.6, minWidth: 42, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
            {i + 1}/{frames.length}
          </span>
        </div>
      ) : null}
    </div>
  );
}

function CovBadge({ level }: { level: "full" | "partial" | "none" }) {
  const map = {
    full: { t: "✅", bg: "rgba(139,212,80,0.16)", c: "#8bd450" },
    partial: { t: "⚠️", bg: "rgba(224,180,80,0.16)", c: "#e0b450" },
    none: { t: "❌", bg: "rgba(224,72,63,0.18)", c: "#ff8b81" },
  }[level];
  return <span style={{ fontSize: 11, padding: "1px 6px", borderRadius: 5, background: map.bg, color: map.c }}>{map.t}</span>;
}

function CoverageSection({ rows, onRun }: { rows: CoverageRow[]; onRun: (id: string) => void }) {
  const [open, setOpen] = useState(true);
  if (!rows.length) return null;
  const cell = { padding: "3px 8px", borderBottom: "1px solid #141a27", fontSize: 11.5 } as const;
  const done = rows.filter((r) => r.demoStatus === "demo").length;
  return (
    <section style={{ marginBottom: 20, border: "1px solid #1c2333", borderRadius: 8, background: "#0b0f18" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", cursor: "pointer" }}
        onClick={() => setOpen((v) => !v)}>
        <b style={{ fontSize: 13 }}>{open ? "▾" : "▸"} SoW coverage — Phase 2 &amp; 3 deliverables</b>
        <span style={{ fontSize: 11, opacity: 0.7 }}>{done}/{rows.length} with a demo</span>
        <span style={{ marginLeft: "auto", fontSize: 11, opacity: 0.6 }}>
          <CovBadge level="full" /> done · <CovBadge level="partial" /> partial · <CovBadge level="none" /> not done
        </span>
      </div>
      {open ? (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 640 }}>
            <thead>
              <tr style={{ textAlign: "left", opacity: 0.7 }}>
                <th style={cell}>#</th><th style={cell}>Deliverable</th>
                <th style={cell}>Impl</th><th style={cell}>LLM‑free</th><th style={cell}>Demo</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={`${r.phase}-${r.id}`}>
                  <td style={{ ...cell, whiteSpace: "nowrap", opacity: 0.7 }}>{r.phase} {r.id}</td>
                  <td style={cell}>{r.title}</td>
                  <td style={cell}><CovBadge level={r.implemented} /></td>
                  <td style={cell}><CovBadge level={r.llmFree} /></td>
                  <td style={cell}>
                    {r.demoStatus === "demo" && r.demo ? (
                      <button type="button" onClick={() => onRun(r.demo as string)}
                        style={{ fontSize: 10.5, padding: "1px 8px", borderRadius: 5, cursor: "pointer",
                                 background: "rgba(139,212,80,0.16)", color: "#8bd450", border: "1px solid rgba(139,212,80,0.3)" }}>
                        ▶ {r.demo}
                      </button>
                    ) : r.demoStatus === "no-demo" ? (
                      <span style={{ fontSize: 10.5, padding: "1px 6px", borderRadius: 5, background: "rgba(148,163,184,0.14)", color: "#94a3b8" }}>NO DEMO</span>
                    ) : (
                      <span style={{ fontSize: 10.5, padding: "1px 6px", borderRadius: 5, background: "rgba(224,72,63,0.18)", color: "#ff8b81" }}>NOT DONE</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

function DemoCard({ demo, onRun, onStep, onClear, onToggle, onSeek, running, flash, recordings, source, onSelectSource, storeMode, onSetStoreMode }: {
  demo: Demo; onRun: (id: string) => void; onStep: (id: string) => void;
  onClear: (id: string) => void; onToggle: (id: string, playing: boolean) => void;
  onSeek: (id: string, index: number) => void; running: boolean; flash?: boolean;
  recordings?: Ls20Recording[]; source?: string | null; onSelectSource?: (key: string) => void;
  storeMode?: string; onSetStoreMode?: (v: string) => void;
}) {
  const frames = (demo.frames && demo.frames.length ? demo.frames : demo.panels) || [];
  const notRun = !!demo.notRun;
  const btn = { fontSize: 11, padding: "3px 10px", borderRadius: 5, cursor: "pointer" } as const;
  return (
    <div id={`demo-${demo.id}`} style={{
      border: flash ? "1px solid #8bd450" : "1px solid #1c2333", borderRadius: 8, padding: 12,
      background: notRun ? "#0b0f18" : "#0d1320",
      display: "flex", flexDirection: "column", gap: 8, opacity: notRun ? 0.82 : 1,
      boxShadow: flash ? "0 0 0 2px rgba(139,212,80,0.55)" : undefined,
      transition: "box-shadow 0.25s, border-color 0.25s",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{
          fontSize: 10.5, fontWeight: 800, letterSpacing: "0.04em", padding: "2px 8px", borderRadius: 5,
          background: notRun ? "rgba(148,163,184,0.16)" : demo.passed ? "rgba(139,212,80,0.18)" : "rgba(224,72,63,0.2)",
          color: notRun ? "#94a3b8" : demo.passed ? "#8bd450" : "#ff8b81",
        }}>{running ? "RUNNING" : notRun ? "NOT RUN" : demo.passed ? "PASS" : "FAIL"}</span>
        <b style={{ flex: 1 }}>{demo.title}</b>
        {running ? <span style={{ fontSize: 11, opacity: 0.6, marginRight: 2 }}>running…</span> : null}
        <button type="button" onClick={() => onRun(demo.id)} style={btn}>▶ Run</button>
        <button type="button" onClick={() => onStep(demo.id)} title="Restart, then step frame by frame"
          style={btn}>▶❙ Run Stepped</button>
        <button type="button" onClick={() => onClear(demo.id)} disabled={notRun && !running}
          title="Stop and clear back to the beginning" style={btn}>Clear</button>
      </div>
      {demo.id === "live-ls20" && recordings && recordings.length ? (
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11.5 }}>
          <span style={{ opacity: 0.7 }}>Recording:</span>
          <select value={source || ""} onChange={(e) => onSelectSource?.(e.target.value)}
            style={{ fontSize: 11.5, padding: "3px 6px", borderRadius: 5, maxWidth: 460,
                     background: "#0b1220", color: "#cfe", border: "1px solid #2a3346" }}>
            {recordings.map((r) => (
              <option key={r.key} value={r.key}>{r.label}</option>
            ))}
          </select>
          <span style={{ opacity: 0.5 }}>choose which ls20 playthrough to learn from</span>
          <label style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 5, opacity: 0.85 }}
            title="Where recognized object memory is saved. none = ephemeral (nothing on disk); recording = this recording's own isolated store; base = a shared long-term demo brain that accumulates across ALL ls20 recordings; canonical = the real production registry (explicit).">
            <span style={{ opacity: 0.7 }}>store:</span>
            <select value={storeMode || "recording"} onChange={(e) => onSetStoreMode?.(e.target.value)}
              style={{ fontSize: 11.5, padding: "3px 6px", borderRadius: 5,
                       background: "#0b1220", color: "#cfe", border: "1px solid #2a3346" }}>
              <option value="none">none (ephemeral)</option>
              <option value="recording">this recording (isolated)</option>
              <option value="base">shared long-term base</option>
              <option value="canonical">canonical registry</option>
            </select>
          </label>
        </div>
      ) : null}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "center", flex: "0 0 auto" }}>
          {notRun
            ? (demo.preview ? <GridPanel panel={demo.preview} /> : <BlankMap />)
            : <AnimatedGrid frames={frames} index={demo.frameIndex || 0} playing={!!demo.playing}
                onToggle={(p) => onToggle(demo.id, p)} onSeek={(idx) => onSeek(demo.id, idx)} />}
          {notRun ? (
            <PreRunControls onRun={() => onRun(demo.id)} onStep={() => onStep(demo.id)} disabled={running} />
          ) : null}
        </div>
        <div style={{ flex: "1 1 240px", minWidth: 220, display: "flex", flexDirection: "column", gap: 8 }}>
          {demo.description ? <div style={{ fontSize: 11.5, opacity: 0.72, lineHeight: 1.4 }}>{demo.description}</div> : null}
          {notRun ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, minHeight: 22 }}>
              {(demo.resultKeys && demo.resultKeys.length ? demo.resultKeys : ["result"]).map((k) => (
                <span key={k} style={{
                  fontSize: 11, padding: "2px 7px", borderRadius: 5, background: "rgba(148,163,184,0.06)",
                  border: "1px dashed rgba(148,163,184,0.25)", color: "#94a3b8",
                }}>
                  <span style={{ opacity: 0.7 }}>{k}:</span> <b>—</b>
                </span>
              ))}
            </div>
          ) : (
            <ResultChips result={demo.result} />
          )}
        </div>
      </div>
    </div>
  );
}

export function RecognitionDemosPage() {
  const [data, setData] = useState<DemosResponse | null>(null);
  const [heads, setHeads] = useState<Record<string, number>>({});
  const [playingMap, setPlayingMap] = useState<Record<string, boolean>>({});
  const [err, setErr] = useState("");
  const [running, setRunning] = useState(false);
  const [flashId, setFlashId] = useState<string | null>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const [showTop, setShowTop] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const pendingRef = useRef<string[]>([]);
  // Optimistic local mirrors of the two selects so the user's pick sticks instantly
  // (the controlled value otherwise snaps back until the server confirms via state).
  const [sourceSel, setSourceSel] = useState<string>("");
  const [storeSel, setStoreSel] = useState<string>("");

  // Server-OWNED animation over a WebSocket: the server decides each demo's current
  // frame (its playhead is advanced on the server) and PUSHES it; the page renders
  // exactly what it receives. There is NO client-side animation loop — buttons only
  // send commands (run / stop / clear / play / seek), and each demo cooperatively
  // follows the shared server control state.
  useEffect(() => {
    let closed = false;
    let retry: ReturnType<typeof setTimeout> | null = null;
    const connect = () => {
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${proto}://${window.location.host}/workbench/recognition/demos/ws`);
      wsRef.current = ws;
      ws.onopen = () => {
        setErr("");
        const q = pendingRef.current;
        pendingRef.current = [];
        q.forEach((s) => { try { ws.send(s); } catch { /* noop */ } });
      };
      ws.onmessage = (ev) => {
        let m: (DemosResponse & { type: string; heads?: Record<string, number>; playing?: Record<string, boolean>; error?: string });
        try { m = JSON.parse(ev.data); } catch { return; }
        if (m.type === "state") {
          setData(m);
          setRunning(!!m.running);
          const h: Record<string, number> = {};
          const pl: Record<string, boolean> = {};
          (m.demos || []).forEach((d) => {
            if (typeof d.frameIndex === "number") h[d.id] = d.frameIndex;
            pl[d.id] = !!d.playing;
          });
          setHeads(h);
          setPlayingMap(pl);
          setErr("");
        } else if (m.type === "heads") {
          setHeads(m.heads || {});
          setPlayingMap(m.playing || {});
          setRunning(!!m.running);
        } else if (m.type === "error") {
          setErr(String(m.error || "error"));
        }
      };
      ws.onclose = () => { if (wsRef.current === ws) wsRef.current = null; if (!closed) retry = setTimeout(connect, 1000); };
      ws.onerror = () => { try { ws.close(); } catch { /* noop */ } };
    };
    connect();
    return () => { closed = true; if (retry) clearTimeout(retry); try { wsRef.current?.close(); } catch { /* noop */ } };
  }, []);

  // Commands are queued if the socket isn't open yet and flushed on open, so a click
  // right after load is never lost (and never shows a spurious "not connected").
  const send = useCallback((msg: Record<string, unknown>) => {
    const s = JSON.stringify(msg);
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(s);
    else pendingRef.current.push(s);
  }, []);

  const runOne = useCallback((id: string) => send({ cmd: "run", id }), [send]);
  const stepOne = useCallback((id: string) => send({ cmd: "run", id, stepped: true }), [send]);
  const runAll = useCallback(() => send({ cmd: "run" }), [send]);
  const stopAll = useCallback(() => send({ cmd: "stop" }), [send]);
  const clearOne = useCallback((id: string) => send({ cmd: "clear", id }), [send]);
  const clearAll = useCallback(() => send({ cmd: "clear" }), [send]);
  const togglePlay = useCallback((id: string, playing: boolean) => send({ cmd: "play", id, playing }), [send]);
  const seek = useCallback((id: string, index: number) => send({ cmd: "seek", id, index }), [send]);
  const selectSource = useCallback((sourceKey: string) => { setSourceSel(sourceKey); send({ cmd: "select_source", source: sourceKey }); }, [send]);
  const setStoreMode = useCallback((value: string) => { setStoreSel(value); send({ cmd: "set_store_mode", value }); }, [send]);
  useEffect(() => { if (data?.ls20Source) setSourceSel(data.ls20Source); }, [data?.ls20Source]);
  useEffect(() => { if (data?.ls20StoreMode) setStoreSel(data.ls20StoreMode); }, [data?.ls20StoreMode]);

  // Coverage-table ▶ buttons live far above the demo cards, so besides starting the
  // run we scroll the matching card into view and briefly highlight it — otherwise
  // clicking a coverage row appears to do nothing.
  const runFromCoverage = useCallback((id: string) => {
    runOne(id);
    setFlashId(id);
    const scrollTo = () => {
      const el = document.getElementById(`demo-${id}`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    // Re-scroll a few times: the card grows from a stub to a full running card as
    // results arrive, so a single scroll would leave it off-screen.
    [60, 500, 1200].forEach((t) => setTimeout(scrollTo, t));
    setTimeout(() => setFlashId((cur) => (cur === id ? null : cur)), 2200);
  }, [runOne]);

  const anyPlaying = !!data?.anyPlaying || Object.values(playingMap).some(Boolean);

  // Merge the catalog (all available tests) with any results: tests that haven't
  // run yet appear as "not run" stub cards so the user can start them individually.
  // Then overlay the SERVER's live playhead (frame index + playing) for each demo.
  const byId = new Map((data?.demos || []).map((d) => [d.id, d]));
  const catalog = data?.catalog || [];
  const merged: Demo[] = catalog.map(
    (c) => byId.get(c.id) || { ...c, description: "", panels: [], frames: [], result: {}, passed: false, notRun: true },
  );
  (data?.demos || []).forEach((d) => { if (!catalog.some((c) => c.id === d.id)) merged.push(d); });
  merged.forEach((d) => {
    if (heads[d.id] !== undefined) d.frameIndex = heads[d.id];
    if (playingMap[d.id] !== undefined) d.playing = playingMap[d.id];
  });

  const groups = merged.reduce<Record<string, Demo[]>>((acc, d) => {
    (acc[d.group] = acc[d.group] || []).push(d);
    return acc;
  }, {});
  const hasResults = !!data?.demos?.length;

  return (
    <div ref={scrollerRef}
      onScroll={(e) => setShowTop(e.currentTarget.scrollTop > 400)}
      style={{ padding: 16, overflow: "auto", height: "100%", position: "relative" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <h2 style={{ margin: 0 }}>Sanity Tests</h2>
        {data && data.total ? (
          <span style={{
            fontSize: 12, padding: "3px 9px", borderRadius: 6,
            background: data.passed === data.total ? "rgba(139,212,80,0.18)" : "rgba(224,72,63,0.2)",
            color: data.passed === data.total ? "#8bd450" : "#ff8b81",
          }}>{data.passed}/{data.total} passing</span>
        ) : null}
        {running ? <span style={{ fontSize: 12, opacity: 0.7 }}>● running on server…</span> : null}
        <button type="button" onClick={runAll} disabled={running}
          style={{ marginLeft: "auto", fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: "pointer" }}>
          {running ? "Running…" : "▶ Run all on server"}
        </button>
        <button type="button" onClick={stopAll} disabled={!running && !anyPlaying}
          style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: (running || anyPlaying) ? "pointer" : "not-allowed" }}>
          ■ Stop all
        </button>
        <button type="button" onClick={clearAll} disabled={!running && !data?.total}
          style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: "pointer" }}>
          Clear all
        </button>
      </div>
      <p style={{ fontSize: 12, opacity: 0.7, marginTop: 0 }}>
        The server runs each real symbolic_arc Phase-2 acceptance behaviour (SOW Exhibit A Phase 2); this page only
        observes and animates the results. Legend: solid = visible/object,{" "}
        <span style={{ color: "#8bd450" }}>green outline / +</span> = generatively filled or regenerated, dashed <b>?</b> = behind the occluder.
      </p>
      {err ? <div style={{ color: "#ff8b81", fontSize: 12, marginBottom: 8 }}>Error: {err}</div> : null}
      <CoverageSection rows={data?.coverage || []} onRun={runFromCoverage} />
      {running && !hasResults ? <div style={{ opacity: 0.6 }}>Server is running the sanity tests…</div> : null}
      {!running && !hasResults ? (
        <div style={{ opacity: 0.6, padding: "8px 0 14px", fontSize: 12.5 }}>
          Nothing has run yet — press <b>▶ Run all on server</b>, or a single test's <b>▶ Run</b> below.
          Nothing runs on its own.
        </div>
      ) : null}
      {Object.entries(groups).map(([group, demos]) => (
        <section key={group} style={{ marginBottom: 20 }}>
          <h3 style={{ margin: "8px 0", fontSize: 14, opacity: 0.85 }}>{group}</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))", gap: 12 }}>
            {demos.map((d) => {
              const cardRunning = running && (data?.only == null || data?.only === d.id);
              return (
                <DemoCard key={d.id} demo={d} onRun={runOne} onStep={stepOne}
                  onClear={clearOne} onToggle={togglePlay} onSeek={seek}
                  running={cardRunning} flash={flashId === d.id}
                  recordings={data?.ls20Recordings} source={sourceSel || data?.ls20Source}
                  onSelectSource={selectSource}
                  storeMode={storeSel || data?.ls20StoreMode} onSetStoreMode={setStoreMode} />
              );
            })}
          </div>
        </section>
      ))}
      {showTop ? (
        <button type="button" title="Back to top" aria-label="Back to top"
          onClick={() => scrollerRef.current?.scrollTo({ top: 0, behavior: "smooth" })}
          style={{
            position: "fixed", right: 30, bottom: 100, zIndex: 60,
            width: 44, height: 44, borderRadius: 22, cursor: "pointer",
            background: "#12233a", color: "#8bd450", border: "1px solid #2a3346",
            fontSize: 20, fontWeight: 800, lineHeight: 1,
            boxShadow: "0 4px 14px rgba(0,0,0,0.45)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>↑</button>
      ) : null}
    </div>
  );
}
