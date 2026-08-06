import { useEffect, useMemo, useState } from "react";

type RecordFile<T> = {
  path: string;
  source?: "shared" | "workspace";
  workspaceId?: string;
  document?: T;
  error?: string;
};

type PromptDef = {
  kind: "prompt";
  id: string;
  label?: string;
  description?: string;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  text?: string | string[];
  implementationSelection?: {default?: string; variants?: string[]};
  [key: string]: unknown;
};

type PromptImplementation = {
  kind: "prompt_implementation";
  id: string;
  label?: string;
  description?: string;
  implements: string;
  version?: number;
  targets?: string[];
  locale?: string;
  text: string | string[];
  [key: string]: unknown;
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

const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9.]+/g, "_").replace(/^_+|_+$/g, "") || "prompt";

export function PromptHierarchyPanel({workspaceId}: {workspaceId: string}) {
  const [prompts, setPrompts] = useState<RecordFile<PromptDef>[]>([]);
  const [implementations, setImplementations] = useState<RecordFile<PromptImplementation>[]>([]);
  const [selected, setSelected] = useState<RecordFile<PromptDef | PromptImplementation> | null>(null);
  const [source, setSource] = useState("");
  const [targetPath, setTargetPath] = useState<string | null>(null);
  const [resolved, setResolved] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    const payload = await jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/prompt-hierarchy`);
    setPrompts(payload.prompts || []);
    setImplementations(payload.promptImplementations || []);
  };

  useEffect(() => {
    void refresh().catch(reason => setError(String(reason)));
  }, [workspaceId]);

  const byPrompt = useMemo(() => {
    const map = new Map<string, RecordFile<PromptImplementation>[]>();
    for (const prompt of prompts) if (prompt.document) map.set(prompt.document.id, []);
    for (const implementation of implementations) {
      const parent = implementation.document?.implements;
      if (parent) map.get(parent)?.push(implementation);
    }
    return map;
  }, [prompts, implementations]);

  const select = (record: RecordFile<PromptDef | PromptImplementation>) => {
    setSelected(record);
    setSource(record.document ? JSON.stringify(record.document, null, 2) : "");
    setTargetPath(record.source === "workspace" || workspaceId === "shared" ? record.path : null);
    setResolved(null);
  };

  const makeLocal = () => {
    if (!selected?.document || workspaceId === "shared") return;
    setTargetPath(`prompts/${slug(selected.document.id)}.${selected.document.kind}.json`);
  };

  const newPrompt = () => {
    const document: PromptDef = {
      kind: "prompt",
      id: "new_prompt",
      label: "New Prompt",
      inputs: {input: "information"},
      outputs: {output: "information"},
      implementationSelection: {default: "new_prompt.default", variants: ["new_prompt.default"]},
    };
    setSelected({path:"",source:"workspace",workspaceId,document});
    setSource(JSON.stringify(document, null, 2));
    setTargetPath(null);
    setResolved(null);
  };

  const newImplementation = () => {
    const parent = selected?.document?.kind === "prompt"
      ? selected.document.id
      : selected?.document?.kind === "prompt_implementation"
        ? selected.document.implements
        : prompts[0]?.document?.id || "prompt";
    const document: PromptImplementation = {
      kind: "prompt_implementation",
      id: `${parent}.new_variant`,
      label: `${parent} — New Variant`,
      implements: parent,
      version: 1,
      targets: ["generic-chat"],
      text: ["Write the prompt implementation here."],
    };
    setSelected({path:"",source:"workspace",workspaceId,document});
    setSource(JSON.stringify(document, null, 2));
    setTargetPath(null);
    setResolved(null);
  };

  const save = async () => {
    setBusy(true);
    setError(null);
    try {
      const document = JSON.parse(source) as PromptDef | PromptImplementation;
      if (!document.id || !["prompt", "prompt_implementation"].includes(document.kind)) {
        throw new Error("Prompt resource must declare id and kind=prompt or kind=prompt_implementation");
      }
      const path = targetPath || `prompts/${slug(document.id)}.${document.kind}.json`;
      await jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/file`, {
        method: "PUT",
        body: JSON.stringify({path, content: JSON.stringify(document, null, 2)}),
      });
      setTargetPath(path);
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const resolveDefault = async (promptId: string, implementation?: string) => {
    setBusy(true);
    setError(null);
    try {
      const query = implementation ? `?implementation=${encodeURIComponent(implementation)}` : "";
      const payload = await jsonRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/prompts/${encodeURIComponent(promptId)}/resolve${query}`);
      setResolved(payload);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setBusy(false);
    }
  };

  const parentPromptId = selected?.document?.kind === "prompt"
    ? selected.document.id
    : selected?.document?.kind === "prompt_implementation"
      ? selected.document.implements
      : null;

  return <section className="resource-view">
    <div className="resource-heading">
      <div>
        <span>PROMPT CONTRACT SYSTEM</span>
        <h1>Prompt hierarchy</h1>
        <p>Prompts are versionable artifacts with abstract interfaces and model-, language-, or compression-specific implementations.</p>
      </div>
      <div className="studio-actions"><button onClick={newPrompt}>New abstract prompt</button><button onClick={newImplementation}>New implementation</button></div>
    </div>

    {error && <div className="backend-error"><b>Prompt editor</b><span>{error}</span><button onClick={() => setError(null)}>×</button></div>}

    <div style={{display:"grid",gridTemplateColumns:"minmax(380px, 1fr) minmax(430px, 1.2fr)",gap:14}}>
      <div className="resource-table">
        <div className="resource-row resource-head"><span>Prompt / implementation</span><span>Kind</span><span>Target</span><span>Source</span><span>Version</span></div>
        {prompts.map(prompt => {
          const doc = prompt.document;
          const children = doc ? (byPrompt.get(doc.id) || []) : [];
          return <div key={`${prompt.workspaceId}:${prompt.path}`}>
            <button className="resource-row" onClick={() => select(prompt)} onDoubleClick={() => select(prompt)}>
              <b>{doc?.label || doc?.id || prompt.path}</b><code>abstract</code><span>{doc?.implementationSelection?.default || "inline"}</span><span>{prompt.source}</span><em>contract</em>
            </button>
            {children.map(child => <button className="resource-row" style={{paddingLeft:28}} key={`${child.workspaceId}:${child.path}`} onClick={() => select(child)} onDoubleClick={() => select(child)}>
              <b>↳ {child.document?.label || child.document?.id || child.path}</b><code>implementation</code><span>{(child.document?.targets || []).join(", ") || "generic"}</span><span>{child.source}</span><em>v{child.document?.version || 1}</em>
            </button>)}
          </div>;
        })}
        {!prompts.length && <div className="studio-empty">No prompt definitions found in the effective workspace.</div>}
      </div>

      <div className="prompt-preview">
        <div>
          <span>{selected?.document?.kind === "prompt_implementation" ? "PROMPT IMPLEMENTATION" : "ABSTRACT PROMPT"}</span>
          <b>{selected?.document?.id || "Select a prompt"}</b>
          <small>{selected?.path || "Double-click a prompt or implementation to edit it."}</small>
          {parentPromptId && <><span>ABSTRACT CONTRACT</span><small>{parentPromptId}</small></>}
          <div className="studio-actions">
            {selected?.source === "shared" && workspaceId !== "shared" && <button onClick={makeLocal}>Make workspace override</button>}
            {parentPromptId && <button disabled={busy} onClick={() => resolveDefault(parentPromptId, selected?.document?.kind === "prompt_implementation" ? selected.document.id : undefined)}>Resolve</button>}
            <button className="primary" disabled={!selected || busy} onClick={save}>Save</button>
          </div>
        </div>
        <textarea className="raw-json-editor" style={{height:380,margin:0,border:0}} value={source} onChange={event => setSource(event.target.value)} placeholder="Select a prompt resource to edit it."/>
        {resolved && <pre className="mini-code" style={{margin:12}}>{JSON.stringify(resolved, null, 2)}</pre>}
      </div>
    </div>
  </section>;
}
