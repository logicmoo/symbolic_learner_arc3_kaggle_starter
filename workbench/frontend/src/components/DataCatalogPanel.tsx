import { useEffect, useMemo, useState } from "react";

type RecordFile<T> = {
  path: string;
  source?: "shared" | "workspace";
  workspaceId?: string;
  document?: T;
  error?: string;
};

type DatatypeDef = {
  kind: "datatype";
  id: string;
  label?: string;
  description?: string;
  extends?: string[];
  representationSelection?: {default?: string; variants?: string[]};
  [key: string]: unknown;
};

type RepresentationDef = {
  kind: "datatype_representation";
  id: string;
  label?: string;
  description?: string;
  implements: string | string[];
  [key: string]: unknown;
};

type ConversionEdge = {
  taskId: string;
  label?: string;
  datatype: string;
  from: string;
  to: string;
  cost: number;
  lossy?: boolean;
  expectedAccuracy?: number;
};

type InventoryRef = {
  ownerKind: string;
  ownerId: string;
  direction: string;
  port: string;
  datatype: string;
  representation?: string | null;
};

async function jsonRequest(path: string, init?: RequestInit) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json", ...(init?.headers || {})},
    ...init,
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(String(payload.error || payload.detail || response.statusText));
  return payload;
}

const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "item";
const implementsType = (representation: RepresentationDef, datatypeId: string) => {
  const value = representation.implements;
  return Array.isArray(value) ? value.includes(datatypeId) : value === datatypeId;
};

export function DataCatalogPanel({workspaceId}: {workspaceId: string}) {
  const [datatypes, setDatatypes] = useState<RecordFile<DatatypeDef>[]>([]);
  const [representations, setRepresentations] = useState<RecordFile<RepresentationDef>[]>([]);
  const [edges, setEdges] = useState<ConversionEdge[]>([]);
  const [references, setReferences] = useState<InventoryRef[]>([]);
  const [undeclaredDatatypes, setUndeclaredDatatypes] = useState<string[]>([]);
  const [undeclaredRepresentations, setUndeclaredRepresentations] = useState<string[]>([]);
  const [selected, setSelected] = useState<RecordFile<DatatypeDef | RepresentationDef> | null>(null);
  const [source, setSource] = useState("");
  const [targetPath, setTargetPath] = useState<string | null>(null);
  const [tab, setTab] = useState<"types" | "conversions" | "usage">("types");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    const [graph, inventory] = await Promise.all([
      jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/representation-graph`),
      jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/data-inventory`),
    ]);
    setDatatypes(graph.datatypes || []);
    setRepresentations(graph.representations || []);
    setEdges(graph.conversionEdges || []);
    setReferences(inventory.references || []);
    setUndeclaredDatatypes(inventory.undeclaredDatatypes || []);
    setUndeclaredRepresentations(inventory.undeclaredRepresentations || []);
  };

  useEffect(() => {
    void refresh().catch(reason => setError(String(reason)));
  }, [workspaceId]);

  const byDatatype = useMemo(() => {
    const result = new Map<string, RecordFile<RepresentationDef>[]>();
    for (const datatype of datatypes) result.set(datatype.document?.id || datatype.path, []);
    for (const representation of representations) {
      if (!representation.document) continue;
      for (const datatype of datatypes) {
        const id = datatype.document?.id;
        if (id && implementsType(representation.document, id)) result.get(id)?.push(representation);
      }
    }
    return result;
  }, [datatypes, representations]);

  const selectRecord = (record: RecordFile<DatatypeDef | RepresentationDef>) => {
    setSelected(record);
    setSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setTargetPath(record.source === "workspace" || workspaceId === "shared" ? record.path : null);
  };

  const makeLocal = () => {
    if (!selected?.document || workspaceId === "shared") return;
    const doc = selected.document;
    const directory = doc.kind === "datatype" ? "datatypes" : "representations";
    setTargetPath(`${directory}/${slug(doc.id)}.${doc.kind}.json`);
  };

  const save = async () => {
    if (!source.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const document = JSON.parse(source) as DatatypeDef | RepresentationDef;
      if (!document.id || !["datatype", "datatype_representation"].includes(document.kind)) {
        throw new Error("Data resource must declare id and kind=datatype or kind=datatype_representation");
      }
      const directory = document.kind === "datatype" ? "datatypes" : "representations";
      const path = targetPath || `${directory}/${slug(document.id)}.${document.kind}.json`;
      await jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {
        method: "PUT",
        body: JSON.stringify({path, content: JSON.stringify(document, null, 2)}),
      });
      await refresh();
      setTargetPath(path);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const selectedId = selected?.document?.id;
  const selectedRefs = references.filter(ref => ref.datatype === selectedId || ref.representation === selectedId);

  return <section className="resource-view">
    <div className="resource-heading">
      <div>
        <span>DATA CONTRACT SYSTEM</span>
        <h1>Datatypes & representations</h1>
        <p>Abstract meaning is separate from concrete encoding. Every type used by tasks, prompts, and workflows is inventoried here.</p>
      </div>
      <div className="studio-actions">
        <button className={tab === "types" ? "primary" : ""} onClick={() => setTab("types")}>Hierarchy</button>
        <button className={tab === "conversions" ? "primary" : ""} onClick={() => setTab("conversions")}>Conversions</button>
        <button className={tab === "usage" ? "primary" : ""} onClick={() => setTab("usage")}>Usage</button>
      </div>
    </div>

    {error && <div className="backend-error"><b>Data editor</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}

    {(undeclaredDatatypes.length > 0 || undeclaredRepresentations.length > 0) && <div className="demo-notice">
      <b>Interface references still need first-class definitions</b>
      <span>{undeclaredDatatypes.length ? `Datatypes: ${undeclaredDatatypes.join(", ")}. ` : ""}{undeclaredRepresentations.length ? `Representations: ${undeclaredRepresentations.join(", ")}.` : ""}</span>
    </div>}

    {tab === "types" && <div style={{display:"grid",gridTemplateColumns:"minmax(360px, 1fr) minmax(420px, 1.15fr)",gap:14}}>
      <div className="resource-table">
        <div className="resource-row resource-head"><span>Abstract datatype / representation</span><span>Kind</span><span>Source</span><span>Default</span><span>State</span></div>
        {datatypes.map(datatype => {
          const doc = datatype.document;
          const children = doc ? (byDatatype.get(doc.id) || []) : [];
          return <div key={`${datatype.workspaceId}:${datatype.path}`}>
            <button className="resource-row" onDoubleClick={() => selectRecord(datatype)} onClick={() => selectRecord(datatype)}>
              <b>{doc?.label || doc?.id || datatype.path}</b><code>datatype</code><span>{datatype.source}</span><span>{doc?.representationSelection?.default || "—"}</span><em>{datatype.error ? "error" : "abstract"}</em>
            </button>
            {children.map(rep => <button className="resource-row" style={{paddingLeft:28}} key={`${rep.workspaceId}:${rep.path}`} onDoubleClick={() => selectRecord(rep)} onClick={() => selectRecord(rep)}>
              <b>↳ {rep.document?.label || rep.document?.id || rep.path}</b><code>representation</code><span>{rep.source}</span><span>{rep.document?.id}</span><em>{rep.error ? "error" : "implementation"}</em>
            </button>)}
          </div>;
        })}
      </div>
      <div className="prompt-preview">
        <div>
          <span>DATA RESOURCE EDITOR</span>
          <b>{selected?.document?.id || "Select a datatype or representation"}</b>
          <small>{selected?.path || "Double-click or select an item in the hierarchy."}</small>
          {selected?.document && <><span>USED BY</span><small>{selectedRefs.length ? `${selectedRefs.length} interface reference(s)` : "No discovered interface references"}</small></>}
          <div className="studio-actions">
            {selected?.source === "shared" && workspaceId !== "shared" && <button onClick={makeLocal}>Make workspace override</button>}
            <button className="primary" disabled={!selected || busy} onClick={save}>Save</button>
          </div>
        </div>
        <textarea className="raw-json-editor" style={{height:420,margin:0,border:0}} value={source} onChange={event => setSource(event.target.value)} placeholder="Select a data resource to edit it."/>
      </div>
    </div>}

    {tab === "conversions" && <div className="resource-table">
      <div className="resource-row resource-head"><span>Conversion task</span><span>Datatype</span><span>From</span><span>To</span><span>Planning</span></div>
      {edges.map(edge => <div className="resource-row" key={`${edge.taskId}:${edge.from}:${edge.to}`}><b>{edge.label || edge.taskId}</b><code>{edge.datatype}</code><span>{edge.from}</span><span>{edge.to}</span><em>cost {edge.cost}{edge.lossy ? " · lossy" : ""}</em></div>)}
      {!edges.length && <div className="studio-empty">No representation conversion tasks are currently declared.</div>}
    </div>}

    {tab === "usage" && <div className="resource-table">
      <div className="resource-row resource-head"><span>Owner</span><span>Kind</span><span>Port</span><span>Datatype</span><span>Representation</span></div>
      {references.map((ref, index) => <div className="resource-row" key={`${ref.ownerKind}:${ref.ownerId}:${ref.port}:${index}`}><b>{ref.ownerId}</b><code>{ref.ownerKind}</code><span>{ref.direction}:{ref.port}</span><span>{ref.datatype}</span><em>{ref.representation || "planner-selected"}</em></div>)}
    </div>}
  </section>;
}
