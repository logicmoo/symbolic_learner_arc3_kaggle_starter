import { useEffect, useState } from "react";

type Workspace = {
  id: string;
  label: string;
  description: string;
  root: string;
  workflowFileCount: number;
  taskFileCount: number;
  datatypeFileCount?: number;
  representationFileCount?: number;
  modelFileCount?: number;
  promptFileCount?: number;
};

type DataInventory = {
  undeclaredDatatypes?: string[];
  undeclaredRepresentations?: string[];
  references?: Array<{
    ownerKind: string;
    ownerId: string;
    direction: string;
    port: string;
    datatype: string;
    representation?: string | null;
  }>;
};

async function request(path: string) {
  const response = await fetch(path);
  const payload = await response.json();
  if (!response.ok) throw new Error(String(payload.error || payload.detail || response.statusText));
  return payload;
}

export function WorkspaceSetupPanel({
  workspace,
  workspaces,
  implementationCount,
  editableFileCount,
  onChooseWorkspace,
}: {
  workspace: Workspace;
  workspaces: Workspace[];
  implementationCount: number;
  editableFileCount: number;
  onChooseWorkspace: (workspace: Workspace) => void;
}) {
  const [inventory, setInventory] = useState<DataInventory | null>(null);
  const [workspaceRoots, setWorkspaceRoots] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      request("/api/workspaces"),
      request(`/api/workspaces/${encodeURIComponent(workspace.id)}/data-inventory`),
    ]).then(([workspacePayload, inventoryPayload]) => {
      if (cancelled) return;
      setWorkspaceRoots((workspacePayload.workspaceRoots || []) as string[]);
      setInventory(inventoryPayload as DataInventory);
      setError(null);
    }).catch(reason => {
      if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason));
    });
    return () => { cancelled = true; };
  }, [workspace.id]);

  const missingTypes = inventory?.undeclaredDatatypes || [];
  const missingRepresentations = inventory?.undeclaredRepresentations || [];
  const referenceCount = inventory?.references?.length || 0;

  return <section className="resource-view">
    <div className="resource-heading">
      <div>
        <span>WORKSPACE SETUP</span>
        <h1>{workspace.label}</h1>
        <p>{workspace.root}</p>
      </div>
    </div>

    {error && <div className="backend-error"><b>Setup inventory</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}

    <div className="settings-grid">
      <label><span>WORKSPACE TYPE</span><select value={workspace.id === "shared" ? "shared" : "project"} disabled><option value="shared">Shared library</option><option value="project">Project workspace</option></select><small>{editableFileCount} editable text files discovered from disk.</small></label>
      <label><span>ENGINE IMPLEMENTATIONS</span><select value={implementationCount} disabled><option value={implementationCount}>{implementationCount} registered implementations</option></select><small>Registered by the running workflow engine.</small></label>
      <label><span>DATA CONTRACT REFERENCES</span><input value={referenceCount} readOnly/><small>Task, prompt, and workflow ports inventoried against first-class datatypes.</small></label>
      <label><span>DISCOVERED WORKSPACE ROOTS</span><input value={workspaceRoots.length} readOnly/><small>{workspaceRoots.join(" · ") || "No workspace roots returned"}</small></label>
    </div>

    <div className="resource-heading" style={{marginTop:16}}>
      <div><span>VISIBLE WORKSPACES</span><h2>Filesystem workspaces this instance can see</h2><p>This is the same directory enumeration used by the workspace chooser. Shared is a real editable workspace and normal workspaces inherit from it.</p></div>
    </div>
    <div className="resource-table">
      <div className="resource-row resource-head"><span>Workspace</span><span>Role</span><span>Resources</span><span>Root</span><span>State</span></div>
      {workspaces.map(item => <button className="resource-row" key={item.root} onClick={() => onChooseWorkspace(item)}>
        <b>{item.label}</b>
        <code>{item.id === "shared" ? "shared library" : "project"}</code>
        <span>{item.workflowFileCount || 0} wf · {item.taskFileCount || 0} tasks · {item.datatypeFileCount || 0} types · {item.representationFileCount || 0} reps · {item.modelFileCount || 0} models · {item.promptFileCount || 0} prompts</span>
        <span>{item.root}</span>
        <em>{item.id === workspace.id ? "current" : "open"}</em>
      </button>)}
    </div>

    <div className="resource-heading" style={{marginTop:16}}>
      <div><span>FIRST-CLASS DATA COVERAGE</span><h2>Referenced interfaces still needing definitions</h2><p>The Data page owns these contracts. Setup keeps the gaps visible so an undeclared type cannot disappear inside a task or workflow.</p></div>
    </div>
    {(missingTypes.length || missingRepresentations.length) ? <div className="demo-notice">
      <b>Interface references still need first-class definitions</b>
      <span>{missingTypes.length ? `Datatypes: ${missingTypes.join(", ")}. ` : ""}{missingRepresentations.length ? `Representations: ${missingRepresentations.join(", ")}.` : ""}</span>
    </div> : <div className="validation good">All discovered datatype and representation references have first-class definitions.</div>}

    <div className="resource-table" style={{marginTop:12}}>
      <div className="resource-row resource-head"><span>Missing item</span><span>Kind</span><span>Owner</span><span>Port</span><span>Action</span></div>
      {missingTypes.map(id => {
        const ref = inventory?.references?.find(item => item.datatype === id);
        return <div className="resource-row" key={`datatype:${id}`}><b>{id}</b><code>datatype</code><span>{ref ? `${ref.ownerKind}:${ref.ownerId}` : "referenced interface"}</span><span>{ref ? `${ref.direction}:${ref.port}` : "—"}</span><em>define under Data</em></div>;
      })}
      {missingRepresentations.map(id => {
        const ref = inventory?.references?.find(item => item.representation === id);
        return <div className="resource-row" key={`representation:${id}`}><b>{id}</b><code>representation</code><span>{ref ? `${ref.ownerKind}:${ref.ownerId}` : "referenced interface"}</span><span>{ref ? `${ref.direction}:${ref.port}` : "—"}</span><em>define under Data</em></div>;
      })}
    </div>
  </section>;
}
