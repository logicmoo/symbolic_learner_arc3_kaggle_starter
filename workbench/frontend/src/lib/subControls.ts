// Sub-control (tab) enumeration API for the Super Control (UniversalArtifactEditor).
// When a control is made it enumerates its tabs from here rather than hardcoding them.
// For now this returns the full list of all known sub-controls. Later, a type/capability
// descriptor can filter this down (see editor_consolidation_plan.md: tabsFor(descriptor)).

export type SubControlDescriptor = {
  /** Stable id used to look up the renderer for this tab. */
  id: string;
  /** Human label shown on the EDITORS tab. */
  label: string;
  /** "builtin" or the contributing plugin id. */
  source?: string;
};

// For now the API returns the full list of surfaces we are eliminating (from
// editor_inventory.md). Each becomes a tab in the Super Control; renderers are wired in
// progressively. Later this list is type/capability filtered and merged with plugin
// contributions fetched over REST.
const SURFACES_BEING_ELIMINATED: SubControlDescriptor[] = [
  { id: "file", label: "File", source: "builtin" },
  { id: "markdown", label: "Markdown", source: "builtin" },
  { id: "resource", label: "Resource", source: "builtin" },
  { id: "inheritance", label: "Inheritance", source: "builtin" },
  { id: "runner", label: "Universal Execution Runner", source: "builtin" },
  { id: "prompt-library", label: "Prompt Library", source: "builtin" },
  { id: "policy-library", label: "Policy Library", source: "builtin" },
  { id: "operation-library", label: "Operation Library", source: "builtin" },
  { id: "goal-plan-library", label: "Goal & Plan Library", source: "builtin" },
  { id: "topics", label: "Topics / Categories", source: "builtin" },
  { id: "models", label: "Models & Presets", source: "builtin" },
  { id: "data-catalog", label: "Data Catalog", source: "builtin" },
  { id: "workflow-page-source", label: "Workflow Page Source", source: "builtin" },
  { id: "workspace-settings", label: "Workspace Settings", source: "builtin" },
  { id: "model-policy", label: "Model Policy", source: "builtin" },
  { id: "load-text-documents", label: "Load Text Documents", source: "builtin" },
  { id: "chat-entry", label: "Chat: Entry", source: "builtin" },
  { id: "chat-config", label: "Chat: Config", source: "builtin" },
  { id: "chat-file", label: "Chat: File Stream", source: "builtin" },
  { id: "chat-inspect", label: "Chat: Inspect", source: "builtin" },
  { id: "workflow-engine", label: "Workflow Engine", source: "builtin" },
  { id: "workspace-workbench", label: "Workspace Workbench", source: "builtin" },
  { id: "real-workspace-desktop", label: "Workspace Desktop", source: "builtin" },
  { id: "workbench-builder", label: "Workflow Builder", source: "builtin" },
  { id: "example-execute", label: "Example Execute", source: "builtin" },
  { id: "model-playground", label: "Model Playground", source: "builtin" },
  { id: "operation-playground", label: "Operation Playground", source: "builtin" },
  { id: "pddl-plan-import", label: "PDDL Plan Import", source: "builtin" },
  { id: "runtime-history", label: "Runtime History", source: "builtin" },
  { id: "plugin-admin", label: "Plugin Admin", source: "builtin" },
  { id: "prompt-hierarchy", label: "Prompt Hierarchy", source: "builtin" },
];

/** Synchronous built-in fallback list. */
export function builtinSubControls(): SubControlDescriptor[] {
  return [...SURFACES_BEING_ELIMINATED];
}

/**
 * The Control calls this over REST to enumerate its sub-controls: the built-in list
 * (for now, the surfaces we are eliminating) merged with any a plugin contributes via
 * `plugin.subControls` on /api/plugins. Falls back to the built-in list on error.
 */
export async function fetchSubControls(): Promise<SubControlDescriptor[]> {
  try {
    const response = await fetch("/api/plugins", { cache: "no-store" });
    if (!response.ok) throw new Error(`plugins ${response.status}`);
    const payload = await response.json();
    const contributed: SubControlDescriptor[] = (payload.plugins || []).flatMap((plugin: { id?: string; subControls?: Array<{ id?: string; label?: string }> }) =>
      (plugin.subControls || []).map(entry => ({ id: String(entry.id), label: String(entry.label || entry.id), source: String(plugin.id || "plugin") })),
    );
    const merged = [...SURFACES_BEING_ELIMINATED];
    for (const entry of contributed) if (entry.id && !merged.some(existing => existing.id === entry.id)) merged.push(entry);
    return merged;
  } catch {
    return [...SURFACES_BEING_ELIMINATED];
  }
}
