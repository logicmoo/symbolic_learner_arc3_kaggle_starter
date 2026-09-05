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
};
type CatalogEntry = { id: string; group: string; title: string; preview?: Panel | null; resultKeys?: string[] };
type CoverageRow = {
  phase: string; id: string; title: string;
  implemented: "full" | "partial" | "none"; llmFree: "full" | "partial" | "none";
  demo: string | null; demoStatus: "demo" | "no-demo" | "not-done";
};
type DemosResponse = {
  demos: Demo[]; total: number; passed: number; running?: boolean; catalog?: CatalogEntry[];
  coverage?: CoverageRow[]; only?: string | null;
};

const CELL = 16;
const MAX_PX = 360;

function GridPanel({ panel }: { panel: Panel }) {
  const px = Math.max(3, Math.min(CELL, Math.floor(MAX_PX / Math.max(panel.w, panel.h, 1))));
  const W = panel.w * px;
  const H = panel.h * px;
  const dense = Math.max(panel.w, panel.h) >= 24;  // big real scenes: draw as a clean bitmap
  return (
    <figure style={{ margin: 0, display: "flex", flexDirection: "column", gap: 4, alignItems: "center" }}>
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
      <figcaption style={{ fontSize: 10.5, opacity: 0.7, textAlign: "center", maxWidth: W + 40 }}>{panel.label}</figcaption>
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

function AnimatedGrid({ frames, autoplay = true, resetToken = 0 }: { frames: Panel[]; autoplay?: boolean; resetToken?: number }) {
  const [i, setI] = useState(0);
  const [playing, setPlaying] = useState(autoplay);
  const multi = frames.length > 1;
  // Restart the animation to the beginning when a new run is triggered for this card.
  useEffect(() => { setI(0); setPlaying(autoplay); }, [resetToken, autoplay]);
  useEffect(() => { if (i > frames.length - 1) setI(0); }, [frames.length, i]);
  useEffect(() => {
    if (!multi || !playing) return;
    const t = setInterval(() => setI((v) => (v + 1) % frames.length), 700);
    return () => clearInterval(t);
  }, [multi, playing, frames.length]);
  if (!frames.length) return <div style={{ opacity: 0.5, fontSize: 12 }}>no frames</div>;
  const cur = frames[Math.min(i, frames.length - 1)];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "center" }}>
      <div style={{ display: "flex", gap: 10, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "center" }}>
        <GridPanel panel={cur} />
        {cur.aux ? <GridPanel panel={cur.aux} /> : null}
      </div>
      {multi ? (
        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
          <button type="button" title="Previous step"
            onClick={() => { setPlaying(false); setI((v) => (v - 1 + frames.length) % frames.length); }}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>◀</button>
          <button type="button" title={playing ? "Pause" : "Play"}
            onClick={() => setPlaying((p) => !p)}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>{playing ? "⏸" : "▶"}</button>
          <button type="button" title="Next step"
            onClick={() => { setPlaying(false); setI((v) => (v + 1) % frames.length); }}
            style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "pointer" }}>▶❙</button>
          <input type="range" min={0} max={frames.length - 1} value={Math.min(i, frames.length - 1)}
            onChange={(e) => { setPlaying(false); setI(Number(e.target.value)); }} style={{ width: 110 }} />
          <span style={{ opacity: 0.6, minWidth: 42, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
            {Math.min(i, frames.length - 1) + 1}/{frames.length}
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

function DemoCard({ demo, onRun, onStep, onClear, running, stepMode, resetToken }: {
  demo: Demo; onRun: (id: string) => void; onStep: (id: string) => void;
  onClear: (id: string) => void; running: boolean; stepMode: boolean; resetToken: number;
}) {
  const frames = (demo.frames && demo.frames.length ? demo.frames : demo.panels) || [];
  const notRun = !!demo.notRun;
  const btn = { fontSize: 11, padding: "3px 10px", borderRadius: 5, cursor: "pointer" } as const;
  return (
    <div style={{
      border: "1px solid #1c2333", borderRadius: 8, padding: 12,
      background: notRun ? "#0b0f18" : "#0d1320",
      display: "flex", flexDirection: "column", gap: 8, opacity: notRun ? 0.82 : 1,
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
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "center", flex: "0 0 auto" }}>
          {notRun
            ? (demo.preview ? <GridPanel panel={demo.preview} /> : <BlankMap />)
            : <AnimatedGrid frames={frames} autoplay={!stepMode} resetToken={resetToken} />}
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
  const [err, setErr] = useState("");
  const [running, setRunning] = useState(false);
  const [stepIds, setStepIds] = useState<Set<string>>(new Set());
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [runNonce, setRunNonce] = useState<Record<string, number>>({});
  const bump = useCallback((id: string) => setRunNonce((m) => ({ ...m, [id]: (m[id] || 0) + 1 })), []);

  // The UI only OBSERVES: it polls the server's cached run. While a run is in
  // progress it polls fast to animate; when idle it keeps polling slowly so a run
  // triggered elsewhere (e.g. by a collaborator on the same page) shows up here too.
  const observe = useCallback(() => {
    fetch("/workbench/recognition/demos")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => {
        setData(d);
        setRunning(!!d.running);
        if (pollRef.current) clearTimeout(pollRef.current);
        pollRef.current = setTimeout(observe, d.running ? 1200 : 3500);
      })
      .catch((e) => setErr(String(e)));
  }, []);

  const runOnServer = useCallback((only?: string) => {
    setErr("");
    setRunning(true);
    fetch("/workbench/recognition/demos/run", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(only ? { only } : {}),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(() => observe())
      .catch((e) => setErr(String(e)));
  }, [observe]);

  // "Run" auto-plays; "Run Stepped" runs then starts PAUSED so you step manually.
  // Both restart the animation to the beginning via the per-card run nonce.
  const runOne = useCallback((id: string) => {
    setStepIds((s) => { const n = new Set(s); n.delete(id); return n; });
    bump(id);
    runOnServer(id);
  }, [runOnServer, bump]);
  const stepOne = useCallback((id: string) => {
    setStepIds((s) => new Set(s).add(id));
    bump(id);
    runOnServer(id);
  }, [runOnServer, bump]);
  const runAll = useCallback(() => runOnServer(), [runOnServer]);

  const stopOnServer = useCallback(() => {
    fetch("/workbench/recognition/demos/stop", { method: "POST" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(() => { setRunning(false); observe(); })
      .catch((e) => setErr(String(e)));
  }, [observe]);

  const clearOnServer = useCallback((only?: string) => {
    if (pollRef.current) clearTimeout(pollRef.current);
    if (only) setStepIds((s) => { const n = new Set(s); n.delete(only); return n; });
    fetch("/workbench/recognition/demos/clear", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(only ? { only } : {}),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => { setRunning(false); setData(d); })
      .catch((e) => setErr(String(e)));
  }, []);
  const clearOne = useCallback((id: string) => clearOnServer(id), [clearOnServer]);
  const clearAll = useCallback(() => clearOnServer(), [clearOnServer]);

  useEffect(() => {
    observe();
    return () => { if (pollRef.current) clearTimeout(pollRef.current); };
  }, [observe]);

  // Merge the catalog (all available tests) with any results: tests that haven't
  // run yet appear as "not run" stub cards so the user can start them individually.
  const byId = new Map((data?.demos || []).map((d) => [d.id, d]));
  const catalog = data?.catalog || [];
  const merged: Demo[] = catalog.map(
    (c) => byId.get(c.id) || { ...c, description: "", panels: [], frames: [], result: {}, passed: false, notRun: true },
  );
  (data?.demos || []).forEach((d) => { if (!catalog.some((c) => c.id === d.id)) merged.push(d); });

  const groups = merged.reduce<Record<string, Demo[]>>((acc, d) => {
    (acc[d.group] = acc[d.group] || []).push(d);
    return acc;
  }, {});
  const hasResults = !!data?.demos?.length;

  return (
    <div style={{ padding: 16, overflow: "auto", height: "100%" }}>
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
        <button type="button" onClick={stopOnServer} disabled={!running}
          style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: running ? "pointer" : "not-allowed" }}>
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
      <CoverageSection rows={data?.coverage || []} onRun={runOne} />
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
                  onClear={clearOne} running={cardRunning} stepMode={stepIds.has(d.id)}
                  resetToken={runNonce[d.id] || 0} />
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
