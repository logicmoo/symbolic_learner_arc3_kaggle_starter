import { useCallback, useEffect, useMemo, useState } from "react";

type Json = Record<string, unknown>;

type Artifact = {
  id: number;
  name: string;
  type: string;
  producer: string;
  value: string;
  confidence: number;
  version: number;
  payload: Json;
  createdAt: string;
};

type Event = {
  id: number;
  kind: string;
  stage: number;
  createdAt: string;
  message: string;
  tone: string;
  payload: Json;
};

type Run = {
  id: string;
  workflowId: string;
  worldId: string;
  episode: number;
  status: string;
  stage: number;
  maxStage: number;
  chosenAction: string | null;
  modelVersion: number;
  artifacts: Artifact[];
  events: Event[];
  cursor: number;
  operation: Json;
};

type Catalog = {
  workflows: Json[];
  operations: Json[];
  datatypes: Json[];
};

const api = async <T,>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(path, { cache: "no-store", ...init });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `${response.status} ${response.statusText}`);
  return payload as T;
};

function JsonPanel({ value }: { value: unknown }) {
  return <pre style={{ whiteSpace: "pre-wrap", overflow: "auto", maxHeight: 440 }}>{JSON.stringify(value, null, 2)}</pre>;
}

export function BackendWorkbenchPage() {
  const [health, setHealth] = useState<Json | null>(null);
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [selectedArtifact, setSelectedArtifact] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"run" | "artifacts" | "events" | "workflows" | "operations" | "datatypes">("run");

  const selected = useMemo(
    () => run?.artifacts.find((artifact) => artifact.id === selectedArtifact) ?? run?.artifacts[0] ?? null,
    [run, selectedArtifact],
  );

  const loadCatalog = useCallback(async () => {
    const payload = await api<Catalog>("/workbench/workflows");
    setCatalog(payload);
  }, []);

  const createRun = useCallback(async () => {
    const payload = await api<{ run: Run }>("/workbench/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflowId: "arc3_human_observation", worldId: "ls20" }),
    });
    setRun(payload.run);
    setSelectedArtifact(payload.run.artifacts[0]?.id ?? null);
  }, []);

  const refreshRun = useCallback(async () => {
    if (!run) return;
    const payload = await api<{ run: Run }>(`/workbench/runs/${run.id}`);
    setRun(payload.run);
  }, [run]);

  const command = useCallback(async (name: string, input: Json = {}) => {
    if (!run || busy) return;
    setBusy(true);
    setError(null);
    try {
      const payload = await api<{ run: Run }>(`/workbench/runs/${run.id}/commands`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: name, input }),
      });
      setRun(payload.run);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setBusy(false);
    }
  }, [busy, run]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [healthPayload] = await Promise.all([
          api<Json>("/workbench/health"),
          loadCatalog(),
        ]);
        if (!cancelled) setHealth(healthPayload);
        if (!cancelled) await createRun();
      } catch (caught) {
        if (!cancelled) setError(caught instanceof Error ? caught.message : String(caught));
      }
    })();
    return () => { cancelled = true; };
  }, [createRun, loadCatalog]);

  useEffect(() => {
    if (!run) return;
    const timer = window.setInterval(() => void refreshRun(), 1500);
    return () => window.clearInterval(timer);
  }, [refreshRun, run?.id]);

  return <main style={{ minHeight: "100vh", background: "#08111d", color: "#dfeaff", fontFamily: "Inter, system-ui, sans-serif", padding: 20 }}>
    <header style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", marginBottom: 18 }}>
      <div>
        <h1 style={{ margin: 0 }}>MeTTaSymbolicLearnerWorkbench</h1>
        <div style={{ opacity: .75 }}>Backend-authoritative mode — no frontend artifact, event, workflow, operation, or datatype mock data</div>
      </div>
      <div style={{ textAlign: "right" }}>
        <div><b>API:</b> {health ? String(health.status) : "connecting"}</div>
        <div><b>Persistence:</b> {health ? String(health.persistence) : "—"}</div>
      </div>
    </header>

    {error && <div style={{ padding: 12, border: "1px solid #ff647c", borderRadius: 8, marginBottom: 14 }}><b>Backend error:</b> {error}</div>}

    <section style={{ display: "grid", gridTemplateColumns: "260px minmax(0, 1fr)", gap: 16 }}>
      <aside style={{ border: "1px solid #27415f", borderRadius: 10, padding: 12 }}>
        <h3>Backend run</h3>
        {run ? <>
          <div><b>ID</b><br/><code>{run.id}</code></div><br/>
          <div><b>Workflow</b><br/>{run.workflowId}</div><br/>
          <div><b>World</b><br/>{run.worldId}</div><br/>
          <div><b>Status</b><br/>{run.status}</div><br/>
          <div><b>Stage</b><br/>{run.stage} / {run.maxStage}</div><br/>
          <div><b>Model version</b><br/>{run.modelVersion}</div>
        </> : <div>Creating run…</div>}
        <hr style={{ borderColor: "#27415f" }}/>
        <button disabled={!run || busy} onClick={() => void command("run_next")}>Run next</button>{" "}
        <button disabled={!run || busy} onClick={() => void command("toggle_pause")}>Pause/resume</button>
        <div style={{ marginTop: 8 }}>
          {['UP','LEFT','DOWN','RIGHT','SPACE'].map(action => <button key={action} disabled={!run || busy} onClick={() => void command("human_action", { action })} style={{ margin: 2 }}>{action}</button>)}
        </div>
        <div style={{ marginTop: 8 }}>
          <button disabled={!run || busy} onClick={() => void command("repeat")}>Repeat</button>{" "}
          <button disabled={!run || busy} onClick={() => void command("conclude")}>Conclude</button>
        </div>
      </aside>

      <section style={{ minWidth: 0 }}>
        <nav style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
          {(["run","artifacts","events","workflows","operations","datatypes"] as const).map(name =>
            <button key={name} onClick={() => setTab(name)} style={{ fontWeight: tab === name ? 700 : 400 }}>{name}</button>
          )}
        </nav>

        <div style={{ border: "1px solid #27415f", borderRadius: 10, padding: 14, minHeight: 520 }}>
          {tab === "run" && <JsonPanel value={run} />}

          {tab === "artifacts" && <div style={{ display: "grid", gridTemplateColumns: "300px minmax(0,1fr)", gap: 12 }}>
            <div>{run?.artifacts.map(artifact => <button key={artifact.id} onClick={() => setSelectedArtifact(artifact.id)} style={{ display: "block", width: "100%", textAlign: "left", marginBottom: 6 }}>
              <b>{artifact.name}</b><br/><small>{artifact.type} · {artifact.producer} · v{artifact.version}</small>
            </button>)}</div>
            <JsonPanel value={selected} />
          </div>}

          {tab === "events" && <JsonPanel value={run?.events ?? []} />}
          {tab === "workflows" && <JsonPanel value={catalog?.workflows ?? []} />}
          {tab === "operations" && <JsonPanel value={catalog?.operations ?? []} />}
          {tab === "datatypes" && <JsonPanel value={catalog?.datatypes ?? []} />}
        </div>
      </section>
    </section>
  </main>;
}
