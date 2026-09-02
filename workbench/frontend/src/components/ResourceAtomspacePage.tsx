import { useEffect, useMemo, useState } from "react";
import "../styles/resource_atomspace.css";

type ResourceAtom = {
  key: string;
  id: string;
  kind: string;
  label: string;
  path: string;
  workspaceId: string;
  source: string;
  declaredEnabled: boolean;
  effectiveEnabled: boolean;
  availability: Record<string, unknown>;
};

type ResourceLink = {
  id: string;
  source: string;
  target: string;
  relationship: string;
};

type CacheMeta = {
  state: "fresh" | "stale" | "building";
  signature: string;
  building: boolean;
  job?: { status?: string; executor?: string | null } | null;
};

type Payload = {
  atoms: ResourceAtom[];
  links: ResourceLink[];
  relationshipFields: string[];
  cache?: CacheMeta;
};

// Instant-load cache: the last graph seen for each workspace, kept for the
// lifetime of the SPA so returning to the page renders immediately while a
// fresh copy is fetched (and rebuilt on the backend if needed) in the
// background.
const RESOURCE_ATOMSPACE_CACHE = new Map<string, Payload>();

type RelationshipView = "all" | "implementation" | "inheritance" | "dependency";

const RELATIONSHIPS: Record<RelationshipView, Set<string> | null> = {
  all: null,
  implementation: new Set(["implements", "implementedBy", "preferredImplementation"]),
  inheritance: new Set(["inheritsFrom", "inheritedBy"]),
  dependency: new Set(["dependsOn", "dependedOnBy"]),
};

async function request(path: string): Promise<Payload> {
  const response = await fetch(path, { cache: "no-store" });
  const payload = await response.json();
  if (!response.ok) throw new Error(String(payload.detail || response.statusText));
  return payload;
}

function atomspaceSource(atoms: ResourceAtom[], links: ResourceLink[]): string {
  const atomLines = atoms.map(atom =>
    `(Resource "${atom.key}" (kind ${atom.kind}) (id "${atom.id}") (enabled ${atom.effectiveEnabled}))`
  );
  const linkLines = links.map(link =>
    `(${link.relationship} "${link.source}" "${link.target}")`
  );
  return [...atomLines, ...linkLines].join("\n");
}

export function ResourceAtomspacePage({ workspaceId }: { workspaceId: string }) {
  const [payload, setPayload] = useState<Payload | null>(null);
  const [error, setError] = useState("");
  const [cacheMeta, setCacheMeta] = useState<CacheMeta | null>(null);
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState("all");
  const [relationshipView, setRelationshipView] = useState<RelationshipView>("all");
  const [selectedKey, setSelectedKey] = useState("");

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;
    const cached = RESOURCE_ATOMSPACE_CACHE.get(workspaceId);
    if (cached) {
      setPayload(cached);
      setCacheMeta(cached.cache || null);
      setSelectedKey(prev => prev || cached.atoms[0]?.key || "");
    } else {
      setPayload(null);
      setCacheMeta(null);
    }
    setError("");
    const load = () => {
      void request(`/workbench/workspaces/${encodeURIComponent(workspaceId)}/resource-atomspace`)
        .then(next => {
          if (cancelled) return;
          RESOURCE_ATOMSPACE_CACHE.set(workspaceId, next);
          setPayload(next);
          setCacheMeta(next.cache || null);
          setSelectedKey(prev => prev || next.atoms[0]?.key || "");
          // Keep polling while the backend is (re)building in the background.
          if (next.cache && (next.cache.building || next.cache.state !== "fresh")) {
            timer = window.setTimeout(load, 4000);
          }
        })
        .catch(reason => {
          if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason));
        });
    };
    load();
    return () => {
      cancelled = true;
      if (timer) window.clearTimeout(timer);
    };
  }, [workspaceId]);

  const kinds = useMemo(
    () => [...new Set((payload?.atoms || []).map(atom => atom.kind))].sort(),
    [payload],
  );
  const visibleAtoms = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return (payload?.atoms || []).filter(atom =>
      (kind === "all" || atom.kind === kind)
      && (!needle || `${atom.kind} ${atom.id} ${atom.label} ${atom.path}`.toLowerCase().includes(needle))
    );
  }, [payload, query, kind]);
  const visibleKeys = useMemo(() => new Set(visibleAtoms.map(atom => atom.key)), [visibleAtoms]);
  const visibleLinks = useMemo(() => {
    const allowed = RELATIONSHIPS[relationshipView];
    return (payload?.links || []).filter(link =>
      (!allowed || allowed.has(link.relationship))
      && (visibleKeys.has(link.source) || visibleKeys.has(link.target))
    );
  }, [payload, relationshipView, visibleKeys]);
  const selected = payload?.atoms.find(atom => atom.key === selectedKey) || visibleAtoms[0] || null;
  const selectedLinks = selected
    ? visibleLinks.filter(link => link.source === selected.key || link.target === selected.key)
    : [];
  const atomsByKey = useMemo(
    () => new Map((payload?.atoms || []).map(atom => [atom.key, atom])),
    [payload],
  );

  if (error) return <section className="resource-view"><div className="backend-error"><b>Resource AtomSpace</b><span>{error}</span></div></section>;
  if (!payload) return <section className="resource-view"><div className="studio-empty">Loading the workspace Resource AtomSpace...</div></section>;

  return <section className="resource-view resource-atomspace-page">
    <div className="resource-heading">
      <div>
        <span>ATOMSPACES / RESOURCE ATOMSPACE</span>
        <h1>All workspace resources</h1>
        <p>Every effective filesystem/runtime resource is an atom. Canonical resource relationships are directed links.</p>
      </div>
      <div className="resource-atomspace-counts">
        <b>{payload.atoms.length} atoms</b>
        <b>{payload.links.length} links</b>
        <b>{kinds.length} kinds</b>
        {cacheMeta && cacheMeta.state !== "fresh" && (
          <b className="resource-atomspace-cache-state" title={`signature ${cacheMeta.signature.slice(0, 12)}`}>
            {cacheMeta.building
              ? `rebuilding${cacheMeta.job?.executor ? ` · ${cacheMeta.job.executor}` : ""}…`
              : "cached"}
          </b>
        )}
      </div>
    </div>

    <div className="resource-atomspace-controls">
      <input value={query} onChange={event => setQuery(event.target.value)} placeholder="Filter atoms by kind, id, label, or path..." />
      <label>KIND<select value={kind} onChange={event => setKind(event.target.value)}><option value="all">All kinds</option>{kinds.map(value => <option key={value} value={value}>{value}</option>)}</select></label>
      <label>RELATIONSHIP<select value={relationshipView} onChange={event => setRelationshipView(event.target.value as RelationshipView)}><option value="all">All canonical links</option><option value="implementation">Implements / Implemented By</option><option value="inheritance">Inherits From / Inherited By</option><option value="dependency">Depends On / Depended On By</option></select></label>
    </div>

    <div className="resource-atomspace-layout">
      <section className="resource-atomspace-atoms">
        <header><b>ATOMS</b><span>{visibleAtoms.length} visible</span></header>
        <div className="resource-atomspace-atom-grid">
          {visibleAtoms.map(atom => <button className={`${atom.key === selected?.key ? "selected " : ""}${atom.effectiveEnabled ? "enabled" : "disabled"}`} onClick={() => setSelectedKey(atom.key)} key={atom.key}>
            <span>{atom.kind}</span>
            <b>{atom.label}</b>
            <code>{atom.id}</code>
            <small>{atom.source} · {atom.path || "unresolved"}</small>
          </button>)}
        </div>
      </section>

      <aside className="resource-atomspace-inspector">
        <header><b>SELECTED ATOM</b><span>{selected?.kind || "none"}</span></header>
        {selected && <>
          <h2>{selected.label}</h2>
          <code>{selected.key}</code>
          <p>{selected.source} · {selected.workspaceId} · {selected.path || "unresolved"}</p>
          <div className="resource-atomspace-state"><span>DECLARED {selected.declaredEnabled ? "ON" : "OFF"}</span><span>EFFECTIVE {selected.effectiveEnabled ? "ON" : "OFF"}</span></div>
          <div className="resource-atomspace-links">
            {selectedLinks.map(link => {
              const outgoing = link.source === selected.key;
              const otherKey = outgoing ? link.target : link.source;
              const other = atomsByKey.get(otherKey);
              return <button key={link.id} onClick={() => other && setSelectedKey(other.key)}>
                <span>{outgoing ? "OUT" : "IN"}</span>
                <b>{link.relationship}</b>
                <code>{other?.label || otherKey}</code>
              </button>;
            })}
            {!selectedLinks.length && <small>No links in this relationship view.</small>}
          </div>
        </>}
      </aside>
    </div>

    <details className="resource-atomspace-source">
      <summary>AtomSpace MeTTa source · {visibleAtoms.length} atoms / {visibleLinks.length} links</summary>
      <pre>{atomspaceSource(visibleAtoms, visibleLinks)}</pre>
    </details>
  </section>;
}
