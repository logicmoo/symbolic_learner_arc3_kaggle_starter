import { useEffect, useMemo, useState } from "react";

type AnalysisObject = {
  id: string;
  name: string;
  color: number;
  colorName: string;
  cells: number[][];
  bounds: number[];
  shape: string;
  pixelCount: number;
  facts: string;
  turtleProgram: string;
};

type Analysis = {
  source: string;
  algorithm: string;
  grid: number[][];
  reconstruction: number[][];
  width: number;
  height: number;
  sha256: string;
  objects: AnalysisObject[];
  objectCount: number;
  prologFacts: string;
  differenceCount: number;
  differences: number[][];
  exactMatch: boolean;
};

const palette: Record<number, string> = {
  0: "#111827", 1: "#2563eb", 2: "#ef4444", 3: "#22c55e", 4: "#facc15",
  5: "#9ca3af", 6: "#d946ef", 7: "#f97316", 8: "#06b6d4", 9: "#92400e",
};

const starterGrid = [
  [0, 0, 0, 0, 0, 0, 0, 0],
  [0, 1, 1, 1, 0, 2, 0, 0],
  [0, 1, 0, 1, 0, 2, 0, 0],
  [0, 1, 1, 1, 0, 2, 2, 0],
  [0, 0, 0, 0, 0, 0, 0, 0],
];

function Grid({ grid, selected, onSelect }: { grid: number[][]; selected?: AnalysisObject; onSelect?: (x: number, y: number) => void }) {
  const selectedCells = useMemo(() => new Set(selected?.cells.map(([x, y]) => `${x}:${y}`) ?? []), [selected]);
  return <div style={{ display: "grid", gridTemplateColumns: `repeat(${grid[0]?.length ?? 0}, 38px)`, gap: 2, padding: 10, background: "#020617", borderRadius: 12, width: "fit-content" }}>
    {grid.flatMap((row, y) => row.map((cell, x) => <button key={`${x}:${y}`} onClick={() => onSelect?.(x, y)} style={{ width: 38, height: 38, border: selectedCells.has(`${x}:${y}`) ? "3px solid white" : "1px solid #334155", background: palette[cell], cursor: onSelect ? "pointer" : "default" }} title={`(${x}, ${y}) color ${cell}`} />))}
  </div>;
}

export function RealWorkbenchPage() {
  const [grid, setGrid] = useState(starterGrid);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [paintColor, setPaintColor] = useState(1);
  const [status, setStatus] = useState("Connecting to backend…");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const selected = analysis?.objects.find(object => object.id === selectedId) ?? analysis?.objects[0];

  const runAnalysis = async (nextGrid = grid) => {
    setBusy(true);
    setError(null);
    try {
      const health = await fetch("/workbench/health", { cache: "no-store" });
      if (!health.ok) throw new Error("FastAPI backend is not responding");
      const response = await fetch("/workbench/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grid: nextGrid }),
      });
      const payload = await response.json() as { analysis?: Analysis; error?: string };
      if (!response.ok || !payload.analysis) throw new Error(payload.error || "Analysis failed");
      setAnalysis(payload.analysis);
      setSelectedId(payload.analysis.objects[0]?.id ?? null);
      setStatus(`Backend analyzed ${payload.analysis.width}×${payload.analysis.height} grid at ${new Date().toLocaleTimeString()}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Backend unavailable");
      setStatus("No backend result loaded");
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => { void runAnalysis(starterGrid); }, []);

  const paint = (x: number, y: number) => {
    const next = grid.map(row => [...row]);
    next[y][x] = paintColor;
    setGrid(next);
  };

  return <main style={{ minHeight: "100vh", background: "#07111f", color: "#e5eefc", fontFamily: "Inter, system-ui, sans-serif", padding: 20 }}>
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
      <div><h1 style={{ margin: 0 }}>MeTTaSymbolicLearnerWorkbench</h1><p style={{ margin: "5px 0 0", color: "#93a4bd" }}>Live backend symbolic pipeline — no frontend mock data</p></div>
      <div style={{ textAlign: "right" }}><strong style={{ color: error ? "#f87171" : "#4ade80" }}>{error ? "BACKEND ERROR" : "BACKEND LIVE"}</strong><div style={{ color: "#93a4bd", fontSize: 13 }}>{status}</div></div>
    </header>

    {error && <div style={{ background: "#3f1218", border: "1px solid #ef4444", padding: 12, borderRadius: 8, marginBottom: 14 }}>{error}. Start FastAPI on port 8000, then retry.</div>}

    <section style={{ display: "grid", gridTemplateColumns: "280px minmax(520px, 1fr) 380px", gap: 16 }}>
      <aside style={panel}>
        <h2 style={heading}>Input editor</h2>
        <p style={muted}>Click a cell to change the actual grid submitted to FastAPI.</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>{Object.keys(palette).map(value => { const n = Number(value); return <button key={n} onClick={() => setPaintColor(n)} style={{ width: 28, height: 28, background: palette[n], border: paintColor === n ? "3px solid white" : "1px solid #475569" }} title={`Paint color ${n}`} />; })}</div>
        <Grid grid={grid} onSelect={paint} />
        <button disabled={busy} onClick={() => void runAnalysis()} style={primaryButton}>{busy ? "Running backend…" : "Run real analysis"}</button>
        <button onClick={() => { setGrid(starterGrid.map(row => [...row])); void runAnalysis(starterGrid); }} style={secondaryButton}>Reset example</button>
      </aside>

      <section style={panel}>
        <h2 style={heading}>Backend reconstruction</h2>
        {analysis ? <>
          <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}><div><h3>Source</h3><Grid grid={analysis.grid} selected={selected} /></div><div><h3>Reconstructed from extracted objects</h3><Grid grid={analysis.reconstruction} selected={selected} /></div></div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginTop: 16 }}>
            <Metric label="Objects" value={String(analysis.objectCount)} />
            <Metric label="Differing cells" value={String(analysis.differenceCount)} />
            <Metric label="Exact match" value={analysis.exactMatch ? "YES" : "NO"} />
            <Metric label="Runtime" value="FastAPI/Python" />
          </div>
          <p style={muted}><b>Algorithm:</b> {analysis.algorithm}</p><p style={muted}><b>SHA-256:</b> <code>{analysis.sha256}</code></p>
          <h3>Detected objects</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 8 }}>{analysis.objects.map(object => <button key={object.id} onClick={() => setSelectedId(object.id)} style={{ textAlign: "left", padding: 10, borderRadius: 8, border: object.id === selected?.id ? "2px solid #60a5fa" : "1px solid #334155", background: "#0f1b2d", color: "inherit" }}><b>{object.name}</b><div style={muted}>{object.shape} · {object.pixelCount} pixels</div><code>{object.id}</code></button>)}</div>
        </> : <p>No backend analysis loaded.</p>}
      </section>

      <aside style={panel}>
        <h2 style={heading}>Symbolic artifact inspector</h2>
        {selected ? <>
          <dl><dt>ID</dt><dd><code>{selected.id}</code></dd><dt>Shape</dt><dd>{selected.shape}</dd><dt>Color</dt><dd>{selected.colorName} ({selected.color})</dd><dt>Bounds</dt><dd>{selected.bounds.join(", ")}</dd></dl>
          <h3>Prolog facts</h3><pre style={code}>{selected.facts}</pre>
          <h3>Turtle program</h3><pre style={code}>{selected.turtleProgram}</pre>
        </> : <p>No object selected.</p>}
        {analysis && <><h3>All generated facts</h3><pre style={{ ...code, maxHeight: 220 }}>{analysis.prologFacts}</pre><p style={muted}>Source: <code>{analysis.source}</code></p></>}
      </aside>
    </section>
  </main>;
}

function Metric({ label, value }: { label: string; value: string }) { return <div style={{ background: "#0b1728", border: "1px solid #26364c", borderRadius: 8, padding: 10 }}><small style={muted}>{label}</small><div style={{ fontSize: 22, fontWeight: 700 }}>{value}</div></div>; }

const panel: React.CSSProperties = { background: "#0b1626", border: "1px solid #26364c", borderRadius: 12, padding: 16, overflow: "auto" };
const heading: React.CSSProperties = { marginTop: 0 };
const muted: React.CSSProperties = { color: "#93a4bd", fontSize: 13 };
const code: React.CSSProperties = { background: "#020617", color: "#c7d2fe", border: "1px solid #26364c", borderRadius: 8, padding: 10, overflow: "auto", whiteSpace: "pre-wrap", fontSize: 12 };
const primaryButton: React.CSSProperties = { width: "100%", marginTop: 14, padding: 11, border: 0, borderRadius: 8, background: "#2563eb", color: "white", fontWeight: 700, cursor: "pointer" };
const secondaryButton: React.CSSProperties = { ...primaryButton, marginTop: 8, background: "#334155" };
