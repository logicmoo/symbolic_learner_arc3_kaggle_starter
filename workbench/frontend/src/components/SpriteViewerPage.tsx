import { useEffect, useMemo, useState } from "react";

/**
 * Sprite Viewer — inspect the entire symbolic object-memory registry:
 * the colorless SHAPE vocabulary (rendered turtles) and, per GAME scope (identity
 * is shared across a game's levels), the persisted identities and placements.
 * The "induction filter" selects which shapes get induction run on them.
 */

type TurtleCmd = { op: string; box?: number[]; fill?: string; outline?: string };
type Turtle = { commands?: TurtleCmd[] };
type Shape = {
  key: string; name: string; box: string; size: number;
  cells: number[][]; composedOf: string[] | null; turtle?: Turtle;
};
type Identity = { key: string; color: string; first: string; last: string; seen: number };
type Placement = { game: string; iid: string; gid: string; moves: number; points: (string | number)[][] };
type Scope = { identities: Identity[]; placements: Placement[] };
type Snapshot = {
  shapeCount: number; shapes: Shape[];
  scopes: Record<string, Scope>; games: string[];
};

function TurtleTile({ turtle, size = 46 }: { turtle?: Turtle; size?: number }) {
  const rects = (turtle?.commands || []).filter((c) => c.op === "rectangle" && c.box);
  const s = size / 1000;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ background: "#0b0f1a", borderRadius: 4 }}>
      {rects.map((c, i) => {
        const [x0, y0, x1, y1] = c.box as number[];
        return (
          <rect key={i} x={x0 * s} y={y0 * s} width={(x1 - x0) * s} height={(y1 - y0) * s}
            fill={c.fill || "#7c9cff"} stroke={c.outline || c.fill || "#7c9cff"} strokeWidth={0.6} />
        );
      })}
    </svg>
  );
}

export function SpriteViewerPage() {
  const [snap, setSnap] = useState<Snapshot | null>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [game, setGame] = useState("");        // "" = all scopes
  const [query, setQuery] = useState("");       // induction filter: which shapes
  const [maxSize, setMaxSize] = useState(0);    // 0 = no cap
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetch("/workbench/registry/snapshot?includeTurtles=true")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: Snapshot) => { if (alive) { setSnap(d); setErr(""); } })
      .catch((e) => { if (alive) setErr(String(e)); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [reloadKey]);

  const shapes = useMemo(() => {
    const all = snap?.shapes || [];
    const q = query.trim().toLowerCase();
    return all.filter((s) =>
      (!q || s.name.toLowerCase().includes(q) || s.box.toLowerCase().includes(q) ||
        (s.composedOf || []).some((p) => p.toLowerCase().includes(q))) &&
      (!maxSize || s.size <= maxSize));
  }, [snap, query, maxSize]);

  const games = snap?.games || [];
  const identities = useMemo<Identity[]>(() => {
    if (!snap) return [];
    if (game) return snap.scopes?.[game]?.identities || [];
    return Object.values(snap.scopes || {}).flatMap((s) => s.identities);
  }, [snap, game]);
  const placements = useMemo<Placement[]>(() => {
    if (!snap) return [];
    if (game) return snap.scopes?.[game]?.placements || [];
    return Object.values(snap.scopes || {}).flatMap((s) => s.placements);
  }, [snap, game]);

  const cell: React.CSSProperties = { padding: "4px 8px", borderBottom: "1px solid #1c2333", fontSize: 12 };

  return (
    <div style={{ padding: 16, color: "#c9d4e5", overflow: "auto", height: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Sprite Viewer</h2>
        <span style={{ opacity: 0.7, fontSize: 12 }}>
          {snap ? `${snap.shapeCount} shapes · ${games.length} game scope(s)` : ""}
        </span>
        <button onClick={() => setReloadKey((k) => k + 1)} style={{ marginLeft: "auto" }}>↻ Refresh</button>
      </div>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <label style={{ fontSize: 12 }}>
          Induction filter (which shapes):{" "}
          <input value={query} onChange={(e) => setQuery(e.target.value)}
            placeholder="name / box / piece…" style={{ width: 200 }} />
        </label>
        <label style={{ fontSize: 12 }}>
          Max cells:{" "}
          <input type="number" min={0} value={maxSize}
            onChange={(e) => setMaxSize(Math.max(0, Number(e.target.value) || 0))} style={{ width: 70 }} />
        </label>
        <label style={{ fontSize: 12 }}>
          Game scope (identity across levels):{" "}
          <select value={game} onChange={(e) => setGame(e.target.value)}>
            <option value="">All games</option>
            {games.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
      </div>

      {loading && <p>Loading registry…</p>}
      {err && <p style={{ color: "#ff8080" }}>Failed to load registry: {err}</p>}

      {snap && (
        <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 2fr) minmax(0, 1fr)", gap: 16 }}>
          <section>
            <h3 style={{ margin: "0 0 8px" }}>Shapes ({shapes.length})</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))", gap: 8 }}>
              {shapes.map((s) => (
                <div key={s.key} title={`${s.name}\n${s.box}\nsize ${s.size}`}
                  style={{ border: "1px solid #1c2333", borderRadius: 6, padding: 8, background: "#111726" }}>
                  <div style={{ display: "flex", justifyContent: "center" }}><TurtleTile turtle={s.turtle} /></div>
                  <div style={{ fontSize: 11, marginTop: 6, wordBreak: "break-word" }}>{s.name}</div>
                  <div style={{ fontSize: 10, opacity: 0.6 }}>{s.size} px</div>
                  {s.composedOf && (
                    <div style={{ fontSize: 10, opacity: 0.7 }}>= {s.composedOf.join(" + ")}</div>
                  )}
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 style={{ margin: "0 0 8px" }}>
              Identities ({identities.length}){game ? ` · ${game}` : ""}
            </h3>
            <div style={{ border: "1px solid #1c2333", borderRadius: 6, overflow: "hidden" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", background: "#0d1320", fontWeight: 600 }}>
                <div style={cell}>color</div><div style={cell}>shape key</div><div style={cell}>seen</div>
              </div>
              {identities.slice(0, 400).map((o, i) => (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto" }}>
                  <div style={cell}>{o.color}</div>
                  <div style={{ ...cell, fontFamily: "monospace" }}>{o.key.slice(0, 10)}</div>
                  <div style={cell}>{o.seen}</div>
                </div>
              ))}
            </div>
            <h3 style={{ margin: "16px 0 8px" }}>Placements ({placements.length})</h3>
            <div style={{ fontSize: 12, opacity: 0.8 }}>
              {placements.slice(0, 20).map((p, i) => (
                <div key={i} style={{ padding: "2px 0" }}>
                  <span style={{ fontFamily: "monospace" }}>{p.iid}</span> — {p.moves} moves
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
