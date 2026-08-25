// Sub-control (tab) enumeration and context-selection API for Super Control.

export type SubControlDescriptor = {
  /** Stable id used to look up the renderer for this tab. */
  id: string;
  /** Human label shown on the EDITORS tab. */
  label: string;
  /** "builtin" or the contributing plugin id. */
  source?: string;
  /** Resource kinds or capabilities for which the selector may return this tab. */
  contexts?: string[];
};

const SURFACES_BEING_ELIMINATED: SubControlDescriptor[] = [
  { id: "file", label: "File", source: "builtin" },
  { id: "markdown", label: "Markdown", source: "builtin" },
  { id: "resource", label: "Resource & Inheritance", source: "builtin" },
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

const RESOURCE_CONTEXT_CONTROL_IDS = new Set(["file", "markdown", "resource", "runner"]);

export type SubControlSelectorContext = {
  resourceKind?: string | null;
  capabilities?: string[];
};

/**
 * Return only controls selected for the current resource context.
 *
 * Core resource editors are available for every parsed resource. Contributed
 * controls opt into CTX by declaring matching resource kinds/capabilities or
 * the wildcard context. Controls without context declarations remain visible
 * through ALL but are not guessed into CTX.
 */
export function selectSubControls(
  available: SubControlDescriptor[],
  context: SubControlSelectorContext,
): SubControlDescriptor[] {
  const tokens = new Set([
    context.resourceKind || "",
    ...(context.capabilities || []),
  ].map(value => value.trim().toLowerCase()).filter(Boolean));
  return available.filter(control => {
    if (RESOURCE_CONTEXT_CONTROL_IDS.has(control.id)) {
      return control.id !== "runner" || Boolean(context.resourceKind);
    }
    return Boolean(control.contexts?.some(value => value === "*" || tokens.has(value.trim().toLowerCase())));
  });
}

/**
 * The Control calls this over REST to enumerate its sub-controls: the built-in list
 * merged with any a plugin contributes via
 * `plugin.subControls` on /api/plugins. Falls back to the built-in list on error.
 */
export async function fetchSubControls(): Promise<SubControlDescriptor[]> {
  try {
    const response = await fetch("/api/plugins", { cache: "no-store" });
    if (!response.ok) throw new Error(`plugins ${response.status}`);
    const payload = await response.json();
    const contributed: SubControlDescriptor[] = (payload.plugins || []).flatMap((plugin: {
      id?: string;
      subControls?: Array<{ id?: string; label?: string; contexts?: string[] }>;
    }) =>
      (plugin.subControls || []).map(entry => ({
        id: String(entry.id),
        label: String(entry.label || entry.id),
        source: String(plugin.id || "plugin"),
        contexts: Array.isArray(entry.contexts) ? entry.contexts.map(String) : undefined,
      })),
    );
    const merged = [...SURFACES_BEING_ELIMINATED];
    for (const entry of contributed) if (entry.id && !merged.some(existing => existing.id === entry.id)) merged.push(entry);
    return merged;
  } catch {
    return [...SURFACES_BEING_ELIMINATED];
  }
}
