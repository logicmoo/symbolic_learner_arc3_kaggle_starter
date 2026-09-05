import { useEffect, useState } from "react";

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
  panels: Panel[]; result: Record<string, unknown>; passed: boolean;
};
type DemosResponse = { demos: Demo[]; total: number; passed: number };

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

function DemoCard({ demo, onRun, running }: { demo: Demo; onRun: (id: string) => void; running: boolean }) {
  return (
    <div style={{
      border: "1px solid #1c2333", borderRadius: 8, padding: 12, background: "#0d1320",
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{
          fontSize: 10.5, fontWeight: 800, letterSpacing: "0.04em", padding: "2px 8px", borderRadius: 5,
          background: demo.passed ? "rgba(139,212,80,0.18)" : "rgba(224,72,63,0.2)",
          color: demo.passed ? "#8bd450" : "#ff8b81",
        }}>{demo.passed ? "PASS" : "FAIL"}</span>
        <b style={{ flex: 1 }}>{demo.title}</b>
        <button type="button" disabled={running} onClick={() => onRun(demo.id)}
          style={{ fontSize: 11, padding: "3px 10px", borderRadius: 5, cursor: "pointer" }}>
          {running ? "…" : "▶ Run"}
        </button>
      </div>
      <div style={{ fontSize: 11.5, opacity: 0.72, lineHeight: 1.4 }}>{demo.description}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "flex-start", padding: "4px 0" }}>
        {demo.panels.map((p, i) => <GridPanel key={i} panel={p} />)}
      </div>
      <ResultChips result={demo.result} />
    </div>
  );
}

export function RecognitionDemosPage() {
  const [data, setData] = useState<DemosResponse | null>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<string | null>(null);

  const runAll = () => {
    setLoading(true);
    setErr("");
    fetch("/workbench/recognition/demos")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => setData(d))
      .catch((e) => setErr(String(e)))
      .finally(() => setLoading(false));
  };

  const runOne = (id: string) => {
    setRunningId(id);
    fetch(`/workbench/recognition/demos?only=${encodeURIComponent(id)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: DemosResponse) => {
        const one = d.demos[0];
        if (one) setData((prev) => prev ? { ...prev, demos: prev.demos.map((x) => (x.id === id ? one : x)) } : prev);
      })
      .catch((e) => setErr(String(e)))
      .finally(() => setRunningId(null));
  };

  useEffect(runAll, []);

  const groups = (data?.demos || []).reduce<Record<string, Demo[]>>((acc, d) => {
    (acc[d.group] = acc[d.group] || []).push(d);
    return acc;
  }, {});

  return (
    <div style={{ padding: 16, overflow: "auto", height: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <h2 style={{ margin: 0 }}>Sanity Tests</h2>
        {data ? (
          <span style={{
            fontSize: 12, padding: "3px 9px", borderRadius: 6,
            background: data.passed === data.total ? "rgba(139,212,80,0.18)" : "rgba(224,72,63,0.2)",
            color: data.passed === data.total ? "#8bd450" : "#ff8b81",
          }}>{data.passed}/{data.total} passing</span>
        ) : null}
        <button type="button" onClick={runAll} disabled={loading}
          style={{ marginLeft: "auto", fontSize: 12, padding: "4px 12px", borderRadius: 6, cursor: "pointer" }}>
          {loading ? "Running…" : "▶ Run all"}
        </button>
      </div>
      <p style={{ fontSize: 12, opacity: 0.7, marginTop: 0 }}>
        Each sanity test runs a real symbolic_arc Phase-2 acceptance behaviour against live code (SOW Exhibit A Phase 2).
        Legend: solid = visible/object, <span style={{ color: "#8bd450" }}>green outline / +</span> = generatively
        filled or regenerated, dashed <b>?</b> = behind the occluder.
      </p>
      {err ? <div style={{ color: "#ff8b81", fontSize: 12, marginBottom: 8 }}>Error: {err}</div> : null}
      {loading && !data ? <div style={{ opacity: 0.6 }}>Running demos…</div> : null}
      {Object.entries(groups).map(([group, demos]) => (
        <section key={group} style={{ marginBottom: 20 }}>
          <h3 style={{ margin: "8px 0", fontSize: 14, opacity: 0.85 }}>{group}</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: 12 }}>
            {demos.map((d) => <DemoCard key={d.id} demo={d} onRun={runOne} running={runningId === d.id} />)}
          </div>
        </section>
      ))}
    </div>
  );
}
