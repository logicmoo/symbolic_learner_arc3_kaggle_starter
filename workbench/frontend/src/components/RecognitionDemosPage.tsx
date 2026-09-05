import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Recognition Demos — runs the symbolic_arc Phase-2 acceptance behaviours
 * (SOW Exhibit A Phase 2) as visual, re-runnable cards: occlusion completion,
 * recolour / resize identity, store-then-recognize, regeneration, replay, and
 * input breadth (raster / simple video). Data comes from the real recognizer via
 * GET /workbench/recognition/demos — no mocks.
 */

type Cell = { x: number; y: number; role: string; color: string | null };
type Panel = { label: string; w: number; h: number; cells: Cell[] };
type Demo = {
  id: string; group: string; title: string; description: string;
  panels: Panel[]; frames?: Panel[]; result: Record<string, unknown>; passed: boolean;
  notRun?: boolean; preview?: Panel | null; resultKeys?: string[];
};
type CatalogEntry = { id: string; group: string; title: string; preview?: Panel | null; resultKeys?: string[] };
type DemosResponse = {
  demos: Demo[]; total: number; passed: number; running?: boolean; catalog?: CatalogEntry[];
};

const CELL = 16;
const MAX_PX = 240;

function GridPanel({ panel }: { panel: Panel }) {
  const px = Math.max(3, Math.min(CELL, Math.floor(MAX_PX / Math.max(panel.w, panel.h, 1))));
  const W = panel.w * px;
  const H = panel.h * px;
  return (
    <figure style={{ margin: 0, display: "flex", flexDirection: "column", gap: 4, alignItems: "center" }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}
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

function InertControls() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, opacity: 0.4 }}>
      <button type="button" disabled style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "not-allowed" }}>◀</button>
      <button type="button" disabled style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "not-allowed" }}>▶</button>
      <button type="button" disabled style={{ fontSize: 11, padding: "1px 8px", borderRadius: 4, cursor: "not-allowed" }}>▶❙</button>
      <input type="range" min={0} max={0} value={0} disabled readOnly style={{ width: 110 }} />
      <span style={{ minWidth: 42, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>0/0</span>
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

function AnimatedGrid({ frames }: { frames: Panel[] }) {
  const [i, setI] = useState(0);
  const [playing, setPlaying] = useState(true);
  const multi = frames.length > 1;
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
      <GridPanel panel={cur} />
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

function DemoCard({ demo, onRun, running }: { demo: Demo; onRun: (id: string) => void; running: boolean }) {
  const frames = (demo.frames && demo.frames.length ? demo.frames : demo.panels) || [];
  const notRun = !!demo.notRun;
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
        }}>{notRun ? "NOT RUN" : demo.passed ? "PASS" : "FAIL"}</span>
        <b style={{ flex: 1 }}>{demo.title}</b>
        <button type="button" disabled={running} onClick={() => onRun(demo.id)}
          style={{ fontSize: 11, padding: "3px 10px", borderRadius: 5, cursor: "pointer" }}>
          {running ? "…" : "▶ Run"}
        </button>
      </div>
      {demo.description ? <div style={{ fontSize: 11.5, opacity: 0.72, lineHeight: 1.4 }}>{demo.description}</div> : null}
      {notRun ? (
        <>
          <div style={{ display: "flex", justifyContent: "center", padding: "4px 0" }}>
            {demo.preview ? <GridPanel panel={demo.preview} /> : <BlankMap />}
          </div>
          <div style={{ display: "flex", justifyContent: "center" }}><InertControls /></div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6, minHeight: 22 }}>
            {(demo.resultKeys && demo.resultKeys.length ? demo.resultKeys : ["result"]).map((k) => (
              <span key={k} style={{
                fontSize: 11, padding: "2px 7px", borderRadius: 5, background: "rgba(148,163,184,0.06)",
                border: "1px dashed rgba(148,163,184,0.25)", color: "#94a3b8",
              }}>
                <span style={{ opacity: 0.7 }}>{k}:</span> <b>—</b>
              </span>
            ))}
          </div>
        </>
      ) : (
        <>
          <div style={{ display: "flex", justifyContent: "center", padding: "4px 0" }}>
            <AnimatedGrid frames={frames} />
          </div>
          <ResultChips result={demo.result} />
        </>
      )}
    </div>
  );
}

export function RecognitionDemosPage() {
  const [data, setData] = useState<DemosResponse | null>(null);
  const [err, setErr] = useState("");
  const [running, setRunning] = useState(false);
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // The UI only OBSERVES: it polls the server's cached run and re-polls while a
  // background run is in progress. It never computes the tests itself.
  const observe = useCallback(() => {
    fetch("/workbench/recognition/demos")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => {
        setData(d);
        setRunning(!!d.running);
        if (pollRef.current) clearTimeout(pollRef.current);
        if (d.running) pollRef.current = setTimeout(observe, 1200);
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

  const runAll = useCallback(() => runOnServer(), [runOnServer]);
  const runOne = useCallback((id: string) => runOnServer(id), [runOnServer]);

  const stopOnServer = useCallback(() => {
    fetch("/workbench/recognition/demos/stop", { method: "POST" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(() => { setRunning(false); observe(); })
      .catch((e) => setErr(String(e)));
  }, [observe]);

  const clearOnServer = useCallback(() => {
    if (pollRef.current) clearTimeout(pollRef.current);
    fetch("/workbench/recognition/demos/clear", { method: "POST" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => { setRunning(false); setData(d); })
      .catch((e) => setErr(String(e)));
  }, []);

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
        {running ? (
          <button type="button" onClick={stopOnServer}
            style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: "pointer" }}>
            ■ Stop
          </button>
        ) : null}
        <button type="button" onClick={clearOnServer} disabled={running || !data?.total}
          style={{ fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: "pointer" }}>
          Clear
        </button>
      </div>
      <p style={{ fontSize: 12, opacity: 0.7, marginTop: 0 }}>
        The server runs each real symbolic_arc Phase-2 acceptance behaviour (SOW Exhibit A Phase 2); this page only
        observes and animates the results. Legend: solid = visible/object,{" "}
        <span style={{ color: "#8bd450" }}>green outline / +</span> = generatively filled or regenerated, dashed <b>?</b> = behind the occluder.
      </p>
      {err ? <div style={{ color: "#ff8b81", fontSize: 12, marginBottom: 8 }}>Error: {err}</div> : null}
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
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: 12 }}>
            {demos.map((d) => <DemoCard key={d.id} demo={d} onRun={runOne} running={running} />)}
          </div>
        </section>
      ))}
    </div>
  );
}
