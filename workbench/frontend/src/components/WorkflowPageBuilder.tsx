import { useEffect, useMemo, useState } from "react";
import {
  WorkflowPageHost,
  type WorkflowPageComponentRegistry,
  type WorkflowPageDefinition,
  type WorkflowPageMemberDefinition,
} from "./WorkflowPageHost";
import "../styles/english_workflow.css";
import "../styles/workflow_page_builder.css";

type Props = {
  initialDefinition?: WorkflowPageDefinition;
};

type ParseResult = {
  definition?: WorkflowPageDefinition;
  error?: string;
  warnings?: string[];
};

function errorMember(id: string, message: string, raw?: unknown): WorkflowPageMemberDefinition {
  return {
    id,
    label: `ERROR · ${message}`,
    component: "WorkflowPageBuilderError",
    initialDisplayMode: "scroll",
    options: { builderError: message, raw },
  };
}

function recoverDefinition(value: unknown): { definition: WorkflowPageDefinition; warnings: string[] } {
  const warnings: string[] = [];
  const document = value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
  if (document.kind !== "workflow_page") warnings.push("kind was missing or was not workflow_page");
  const layout = document.layout && typeof document.layout === "object" && !Array.isArray(document.layout)
    ? document.layout as Record<string, unknown>
    : {};
  if (layout.kind !== "three_column_accordion") warnings.push("layout.kind was missing or was not three_column_accordion");
  const rawColumns = Array.isArray(layout.columns) ? layout.columns : [];
  if (!Array.isArray(layout.columns)) warnings.push("layout.columns was missing or invalid");
  const columns = (["left", "center", "right"] as const).map((columnId) => {
    const matches = rawColumns.filter((rawColumn) => rawColumn && typeof rawColumn === "object" && !Array.isArray(rawColumn)
      && String((rawColumn as Record<string, unknown>).id || "") === columnId) as Record<string, unknown>[];
    const rawColumn = matches[0];
    const columnWarnings: string[] = [];
    if (!rawColumn) columnWarnings.push(`Missing ${columnId} column`);
    if (matches.length > 1) columnWarnings.push(`Duplicate ${columnId} columns; using the first`);
    const rawMembers = Array.isArray(rawColumn?.members) ? rawColumn.members : [];
    if (rawColumn && !Array.isArray(rawColumn.members)) columnWarnings.push(`${columnId} members was missing or invalid`);
    const members = rawMembers.map((rawMember, index): string | WorkflowPageMemberDefinition => {
      if (typeof rawMember === "string" && rawMember.trim()) return rawMember;
      if (!rawMember || typeof rawMember !== "object" || Array.isArray(rawMember)) {
        const message = `${columnId} member ${index + 1} is not an object or component name`;
        warnings.push(message);
        return errorMember(`invalid-${columnId}-${index + 1}`, message, rawMember);
      }
      const member = rawMember as Record<string, unknown>;
      const id = typeof member.id === "string" && member.id.trim() ? member.id : `invalid-${columnId}-${index + 1}`;
      const component = typeof member.component === "string" && member.component.trim() ? member.component : "";
      if (!component || !(typeof member.id === "string" && member.id.trim())) {
        const message = `${columnId} member ${index + 1} requires both id and component`;
        warnings.push(message);
        return errorMember(id, message, rawMember);
      }
      return rawMember as WorkflowPageMemberDefinition;
    });
    columnWarnings.forEach((message, index) => {
      warnings.push(message);
      members.unshift(errorMember(`invalid-${columnId}-column-${index + 1}`, message, rawColumn));
    });
    const role: "data" | "authoring" | "details" | undefined =
      rawColumn?.role === "data" || rawColumn?.role === "authoring" || rawColumn?.role === "details"
        ? rawColumn.role
        : undefined;
    return {
      id: columnId,
      label: String(rawColumn?.label || columnId.toUpperCase()),
      role,
      members,
    };
  });
  return {
    warnings,
    definition: {
      kind: "workflow_page",
      id: typeof document.id === "string" && document.id.trim() ? document.id : "pasted.workflow_page",
      label: typeof document.label === "string" && document.label.trim() ? document.label : "Pasted Workflow Page",
      description: typeof document.description === "string" ? document.description : undefined,
      glyph: typeof document.glyph === "string" ? document.glyph : undefined,
      routeView: typeof document.routeView === "string" ? document.routeView : "workflowPageBuilder",
      renderer: typeof document.renderer === "string" ? document.renderer : "workflow_page_builder_preview",
      layout: { kind: "three_column_accordion", columns },
    },
  };
}

function parseDefinition(source: string): ParseResult {
  if (!source.trim()) return { error: "Paste a workflow_page JSON document to render its columns." };
  try {
    return recoverDefinition(JSON.parse(source));
  } catch (reason) {
    return { error: reason instanceof Error ? reason.message : String(reason) };
  }
}

function metadata(value: unknown) {
  return <pre>{JSON.stringify(value, null, 2)}</pre>;
}

function previewSurface(member: WorkflowPageMemberDefinition) {
  const builderError = typeof member.options?.builderError === "string" ? member.options.builderError : "";
  const bindingDetails = [
    member.binding ? `binding: ${member.binding}` : "",
    member.operation ? `operation: ${member.operation}` : "",
    member.resource ? `${member.resource.kind}: ${member.resource.id}` : "",
  ].filter(Boolean).join(" · ");
  return {
    value: builderError ? "Declaration error" : member.component,
    detail: bindingDetails || "Declarative component preview",
    baseClass: `english-workflow-contract-panel workflow-page-builder-member ${builderError ? "workflow-page-builder-error" : ""}`.trim(),
    scrollSize: "360px",
    content: <section>
      {builderError && <div className="validation bad"><b>RECOVERED COMPONENT ERROR</b><span>{builderError}</span></div>}
      <div className="operation-abstract-summary">
        <div><span>COMPONENT</span><code>{member.component}</code></div>
        <div><span>MEMBER ID</span><code>{member.id}</code></div>
        <div><span>INITIAL MODE</span><code>{member.initialDisplayMode || "scroll"}</code></div>
        <div><span>RESOURCE</span><code>{member.resource ? `${member.resource.kind}:${member.resource.id}` : "None"}</code></div>
      </div>
      {member.inputs && <div><b>INPUT BINDINGS</b>{metadata(member.inputs)}</div>}
      {member.outputs && <div><b>OUTPUT BINDINGS</b>{metadata(member.outputs)}</div>}
      {member.options && <div><b>OPTIONS</b>{metadata(member.options)}</div>}
      {!member.inputs && !member.outputs && !member.options && <p>This member has no declared bindings or options.</p>}
    </section>,
  };
}

function previewRegistry(definition: WorkflowPageDefinition): WorkflowPageComponentRegistry {
  const components = new Set<string>();
  definition.layout.columns.forEach((column) => column.members.forEach((rawMember) => {
    components.add(typeof rawMember === "string" ? rawMember : rawMember.component);
  }));
  return Object.fromEntries([...components].map((component) => [component, previewSurface]));
}

export function WorkflowPageBuilder({ initialDefinition }: Props) {
  const [source, setSource] = useState(() => initialDefinition ? JSON.stringify(initialDefinition, null, 2) : "");
  const [loadedDefinition, setLoadedDefinition] = useState<WorkflowPageDefinition | undefined>(initialDefinition);
  const [initialized, setInitialized] = useState(Boolean(initialDefinition));
  const [message, setMessage] = useState(initialDefinition ? "Filesystem page loaded and initialized." : "Paste JSON, then select LOAD.");
  const [error, setError] = useState("");

  const initialDefinitionSource = initialDefinition ? JSON.stringify(initialDefinition, null, 2) : "";

  useEffect(() => {
    if (initialDefinition) {
      setSource(initialDefinitionSource);
      setLoadedDefinition(initialDefinition);
      setInitialized(true);
      setMessage("Filesystem page loaded and initialized.");
      setError("");
    }
  }, [initialDefinitionSource]);

  const clear = () => {
    setSource("");
    setLoadedDefinition(undefined);
    setInitialized(false);
    setError("");
    setMessage("Page contents cleared. CURRENT PAGE SPECIFICATION remains ready for another document.");
  };

  const load = () => {
    const parsed = parseDefinition(source);
    if (!parsed.definition) {
      setError(parsed.error || "The page specification could not be loaded.");
      setMessage("The previous valid preview was preserved.");
      return;
    }
    setLoadedDefinition(parsed.definition);
    setInitialized(true);
    setError("");
    setMessage(parsed.warnings?.length
      ? `Loaded ${parsed.definition.label} with ${parsed.warnings.length} recovered declaration error${parsed.warnings.length === 1 ? "" : "s"} and initialized valid components.`
      : `Loaded ${parsed.definition.label} and initialized components.`);
  };

  const init = () => {
    if (!loadedDefinition) return;
    setInitialized(true);
    setError("");
    const count = loadedDefinition.layout.columns.reduce((total, column) => total + column.members.length, 0);
    setMessage(`Initialized ${count} declared component${count === 1 ? "" : "s"} for ${loadedDefinition.label}.`);
  };

  const definition = loadedDefinition;
  const registry = useMemo(() => definition
    ? previewRegistry(definition)
    : {}, [definition, initialized]);
  const memberCount = definition?.layout.columns.reduce((total, column) => total + column.members.length, 0) || 0;

  return <section className="workflow-page-builder" aria-label="Workflow Page Builder">
    <header className="workflow-page-builder-header">
      <div><span>WORKFLOW PAGE BUILDER</span><h1>Paste JSON → LOAD structure</h1><p>Build any declarative workflow_page without adding hard-coded React layout.</p></div>
      <div><b>{definition?.label || "No valid page"}</b><small>{memberCount} declared members · {definition ? initialized ? "initialized" : "loaded" : "cleared"}</small></div>
    </header>
    <div className="workflow-page-builder-source">
      <header><label htmlFor="workflow-page-builder-json">CURRENT PAGE SPECIFICATION</label><div><button type="button" onClick={clear}>CLEAR</button><button type="button" className="primary" disabled={!source.trim()} onClick={load}>LOAD</button><button type="button" className="primary" disabled={!definition} onClick={init}>INIT</button></div></header>
      <textarea id="workflow-page-builder-json" aria-label="Current page specification JSON" value={source} onChange={(event) => { setSource(event.target.value); setError(""); setMessage("Draft changed. Select LOAD to construct the UI."); }} spellCheck={false} placeholder="Paste a workflow_page JSON document here" />
      <footer>
        <span className={error ? "validation bad" : "validation good"}>{error ? `Load error: ${error} ${message}` : message}</span>
        {initialDefinition && <button type="button" onClick={() => { setSource(initialDefinitionSource); setError(""); setMessage("Filesystem page restored in the editor. Select LOAD to synchronize the declaration."); }}>Restore filesystem page</button>}
      </footer>
    </div>
    <div className="workflow-page-builder-preview">
      {definition ? <WorkflowPageHost definition={definition} componentRegistry={registry} pageClassName="english-workflow-page workflow-page-builder-rendered" /> : <div className="studio-empty">Paste a valid workflow_page JSON document to render the preview.</div>}
    </div>
  </section>;
}
