import { Component, useEffect, useMemo, useState, type ErrorInfo, type ReactNode } from "react";
import {
  WorkflowPageHost,
  type WorkflowPageComponentRegistry,
  type WorkflowPageDefinition,
  type WorkflowPageMemberDefinition,
  type WorkflowPageMemberSurface,
} from "./WorkflowPageHost";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import "../styles/english_workflow.css";
import "../styles/workflow_page_builder.css";

type Props = {
  initialDefinition?: WorkflowPageDefinition;
  renderDefinition?: (definition: WorkflowPageDefinition) => ReactNode;
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

type HostedDefinitionBoundaryProps = {
  definition: WorkflowPageDefinition;
  children: ReactNode;
};

type HostedDefinitionBoundaryState = {
  error: Error | null;
  stack: string;
};

class HostedDefinitionBoundary extends Component<HostedDefinitionBoundaryProps, HostedDefinitionBoundaryState> {
  constructor(props: HostedDefinitionBoundaryProps) {
    super(props);
    this.state = { error: null, stack: "" };
  }

  static getDerivedStateFromError(error: Error): HostedDefinitionBoundaryState {
    return { error, stack: "" };
  }

  componentDidCatch(_error: Error, info: ErrorInfo) {
    this.setState({ stack: info.componentStack || "" });
  }

  render() {
    if (!this.state.error) return this.props.children;
    const message = this.state.error.message || "Unknown hosted-page render error";
    const constructorMissing = /constructor not found|is not a function|undefined/i.test(message);
    return <section className="english-workflow-contract-panel workflow-page-builder-member workflow-page-builder-error">
      <div className="validation bad">
        <b>{constructorMissing ? "HOSTED PAGE CONSTRUCTOR NOT FOUND" : "HOSTED PAGE RENDER FAILED"}</b>
        <span>{message}</span>
      </div>
      <div className="operation-abstract-summary">
        <div><span>RENDERER</span><code>{this.props.definition.renderer}</code></div>
        <div><span>PAGE ID</span><code>{this.props.definition.id}</code></div>
      </div>
      {!constructorMissing && <pre>{this.state.error.stack || this.state.stack || this.state.error.message}</pre>}
    </section>;
  }
}

export function WorkflowPageBuilder({ initialDefinition, renderDefinition }: Props) {
  const [source, setSource] = useState(() => initialDefinition ? JSON.stringify(initialDefinition, null, 2) : "");
  const [loadedDefinition, setLoadedDefinition] = useState<WorkflowPageDefinition | undefined>(initialDefinition);
  const [sourceValid, setSourceValid] = useState(true);
  const [componentDrafts, setComponentDrafts] = useState<Record<string, string>>({});
  const [memberJsonDrafts, setMemberJsonDrafts] = useState<Record<string, string>>({});
  const [memberJsonErrors, setMemberJsonErrors] = useState<Record<string, string>>({});
  const [memberJsonValid, setMemberJsonValid] = useState<Record<string, boolean>>({});
  const [memberInitClicks, setMemberInitClicks] = useState<Record<string, number>>({});
  const [memberHeaderCollapsed, setMemberHeaderCollapsed] = useState<Record<string, boolean>>({});
  const [memberJsonEditorCollapsed, setMemberJsonEditorCollapsed] = useState<Record<string, boolean>>({});
  const [initialized, setInitialized] = useState(Boolean(initialDefinition));
  const [message, setMessage] = useState(initialDefinition ? "Filesystem page loaded and initialized." : "Paste JSON, then select LOAD.");
  const [error, setError] = useState("");

  const initialDefinitionSource = initialDefinition ? JSON.stringify(initialDefinition, null, 2) : "";

  useEffect(() => {
    if (initialDefinition) {
      setSource(initialDefinitionSource);
      setLoadedDefinition(initialDefinition);
      setSourceValid(true);
      setInitialized(true);
      setMessage("Filesystem page loaded and initialized.");
      setError("");
    }
  }, [initialDefinitionSource]);

  const updateDefinitionSource = (updater: (document: Record<string, unknown>) => boolean): boolean => {
    try {
      const parsed = JSON.parse(source);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        setMessage("Current page source is not a JSON object.");
        return false;
      }
      const document = parsed as Record<string, unknown>;
      const changed = updater(document);
      if (!changed) return false;
      const nextSource = `${JSON.stringify(document, null, 2)}\n`;
      setSource(nextSource);
      const next = parseDefinition(nextSource);
      if (next.definition) {
        setLoadedDefinition(next.definition);
        setError("");
      }
      return true;
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : String(reason));
      return false;
    }
  };

  const updateMemberComponent = (memberId: string, componentName: string) => {
    const nextName = componentName.trim();
    if (!nextName) return;
    const changed = updateDefinitionSource((document) => {
      const layout = document.layout && typeof document.layout === "object" && !Array.isArray(document.layout)
        ? document.layout as Record<string, unknown>
        : null;
      const columns = Array.isArray(layout?.columns) ? layout.columns : [];
      let updated = false;
      columns.forEach((rawColumn) => {
        if (!rawColumn || typeof rawColumn !== "object" || Array.isArray(rawColumn)) return;
        const column = rawColumn as Record<string, unknown>;
        const members = Array.isArray(column.members) ? column.members : [];
        for (let index = 0; index < members.length; index += 1) {
          const rawMember = members[index];
          if (typeof rawMember === "string" && rawMember.trim() === memberId) {
            members[index] = { id: memberId, component: nextName };
            updated = true;
            break;
          }
          if (!rawMember || typeof rawMember !== "object" || Array.isArray(rawMember)) continue;
          const member = rawMember as Record<string, unknown>;
          if (String(member.id || "").trim() !== memberId) continue;
          member.component = nextName;
          updated = true;
          break;
        }
      });
      return updated;
    });
    if (changed) {
      setComponentDrafts((current) => ({ ...current, [memberId]: nextName }));
      setMessage(`Component for ${memberId} changed to ${nextName}.`);
    }
  };

  const applyMemberJson = (memberId: string) => {
    const draft = memberJsonDrafts[memberId];
    if (!draft) return;
    try {
      const parsed = JSON.parse(draft);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("Member JSON must be an object.");
      const member = parsed as Record<string, unknown>;
      if (String(member.id || "").trim() !== memberId) member.id = memberId;
      if (typeof member.component !== "string" || !member.component.trim()) throw new Error("Member JSON must include a component.");
      const changed = updateDefinitionSource((document) => {
        const layout = document.layout && typeof document.layout === "object" && !Array.isArray(document.layout)
          ? document.layout as Record<string, unknown>
          : null;
        const columns = Array.isArray(layout?.columns) ? layout.columns : [];
        for (const rawColumn of columns) {
          if (!rawColumn || typeof rawColumn !== "object" || Array.isArray(rawColumn)) continue;
          const column = rawColumn as Record<string, unknown>;
          const members = Array.isArray(column.members) ? column.members : [];
          for (let index = 0; index < members.length; index += 1) {
            const rawMember = members[index];
            if (typeof rawMember === "string" && rawMember.trim() === memberId) {
              members[index] = member;
              return true;
            }
            if (!rawMember || typeof rawMember !== "object" || Array.isArray(rawMember)) continue;
            if (String((rawMember as Record<string, unknown>).id || "").trim() === memberId) {
              members[index] = member;
              return true;
            }
          }
        }
        return false;
      });
      if (changed) {
        setMemberJsonErrors((current) => ({ ...current, [memberId]: "" }));
        setComponentDrafts((current) => ({ ...current, [memberId]: String(member.component) }));
        setMessage(`Member JSON applied for ${memberId}.`);
      }
    } catch (reason) {
      const messageText = reason instanceof Error ? reason.message : String(reason);
      setMemberJsonErrors((current) => ({ ...current, [memberId]: messageText }));
    }
  };

  const clear = () => {
    setSource("");
    setLoadedDefinition(undefined);
    setSourceValid(true);
    setInitialized(false);
    setMemberHeaderCollapsed({});
    setMemberJsonEditorCollapsed({});
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
  const componentOptions = useMemo(() => {
    if (!definition) return [] as string[];
    const names = new Set<string>();
    definition.layout.columns.forEach((column) => column.members.forEach((rawMember) => {
      const member = typeof rawMember === "string" ? { id: rawMember, component: rawMember } : rawMember;
      const draft = componentDrafts[member.id];
      names.add((draft || member.component || "").trim());
    }));
    return [...names].filter(Boolean).sort((left, right) => left.localeCompare(right));
  }, [definition, componentDrafts]);
  const registry = useMemo<WorkflowPageComponentRegistry>(() => {
    if (!definition) return {};
    const components = new Set<string>();
    definition.layout.columns.forEach((column) => column.members.forEach((rawMember) => {
      const member = typeof rawMember === "string" ? { id: rawMember, component: rawMember } : rawMember;
      const selected = (componentDrafts[member.id] || member.component || "").trim();
      if (selected) components.add(selected);
    }));
    const renderMember = (member: WorkflowPageMemberDefinition, column: { id: string }): WorkflowPageMemberSurface => {
      try {
        const builderError = typeof member.options?.builderError === "string" ? member.options.builderError : "";
        const selectedComponent = (componentDrafts[member.id] || member.component || "").trim();
        const bindingDetails = [
          member.binding ? `binding: ${member.binding}` : "",
          member.operation ? `operation: ${member.operation}` : "",
          member.resource ? `${member.resource.kind}: ${member.resource.id}` : "",
        ].filter(Boolean).join(" · ");
        const draftJson = memberJsonDrafts[member.id] ?? `${JSON.stringify(member, null, 2)}\n`;
        const headerCollapsed = Boolean(memberHeaderCollapsed[member.id]);
        const jsonEditorCollapsed = memberJsonEditorCollapsed[member.id] !== false;
        return {
          value: builderError ? "Declaration error" : selectedComponent,
          detail: bindingDetails || "Component initialization preview",
          baseClass: `english-workflow-contract-panel workflow-page-builder-member ${builderError ? "workflow-page-builder-error" : ""}`.trim(),
          scrollSize: "420px",
          itemHeader: <section className="workflow-page-builder-member-controls">
            <div className="workflow-page-builder-member-header-toggles">
              <button
                type="button"
                className="workflow-page-builder-toggle"
                aria-label={`${headerCollapsed ? "Expand" : "Collapse"} header controls for ${member.id}`}
                onClick={() => setMemberHeaderCollapsed((current) => ({ ...current, [member.id]: !headerCollapsed }))}
              >{headerCollapsed ? "|>" : "v"} HEADER</button>
              <button
                type="button"
                className="workflow-page-builder-toggle"
                aria-label={`${jsonEditorCollapsed ? "Expand" : "Collapse"} member JSON editor for ${member.id}`}
                disabled={headerCollapsed}
                onClick={() => setMemberJsonEditorCollapsed((current) => ({ ...current, [member.id]: !jsonEditorCollapsed }))}
              >{jsonEditorCollapsed ? "|>" : "v"} MEMBER JSON</button>
            </div>
            {!headerCollapsed && <>
              <div className="operation-abstract-summary">
                <div><span>COMPONENT</span><code>{selectedComponent || member.component}</code></div>
                <div><span>MEMBER ID</span><code>{member.id}</code></div>
                <div><span>INITIAL MODE</span><code>{member.initialDisplayMode || "scroll"}</code></div>
                <div><span>RESOURCE</span><code>{member.resource ? `${member.resource.kind}:${member.resource.id}` : "None"}</code></div>
              </div>
              <div className="operation-editor-actions">
                <select
                  aria-label={`Select component constructor for ${member.id}`}
                  value={componentOptions.includes(selectedComponent) ? selectedComponent : "__custom__"}
                  onChange={(event) => {
                    const next = event.target.value;
                    if (next === "__custom__") return;
                    setComponentDrafts((current) => ({ ...current, [member.id]: next }));
                    updateMemberComponent(member.id, next);
                  }}
                >
                  {componentOptions.map((name) => <option key={name} value={name}>{name}</option>)}
                  <option value="__custom__">Custom…</option>
                </select>
                <input
                  aria-label={`Edit component constructor for ${member.id}`}
                  value={selectedComponent}
                  onChange={(event) => setComponentDrafts((current) => ({ ...current, [member.id]: event.target.value }))}
                />
                <button type="button" onClick={() => updateMemberComponent(member.id, selectedComponent)}>Apply Component</button>
                <button type="button" onClick={() => setMemberInitClicks((current) => ({ ...current, [member.id]: (current[member.id] || 0) + 1 }))}>INIT</button>
              </div>
              <div className="workflow-page-builder-member-json-editor">
                {!jsonEditorCollapsed && <ResourceSourceEditor
                  value={draftJson}
                  onChange={(value) => {
                    setMemberJsonDrafts((current) => ({ ...current, [member.id]: value }));
                    setMemberJsonErrors((current) => ({ ...current, [member.id]: "" }));
                  }}
                  onValidityChange={(valid) => setMemberJsonValid((current) => ({ ...current, [member.id]: valid }))}
                  className="workflow-page-builder-member-source-editor"
                  label={`Edit member ${member.id} (MeTTa/JSON/Tree)`}
                  showEnablement={false}
                />}
                <div className="operation-editor-actions">
                  <button type="button" disabled={memberJsonValid[member.id] === false} onClick={() => applyMemberJson(member.id)}>Apply Member JSON</button>
                </div>
              </div>
            </>}
          </section>,
          content: <section className="workflow-page-builder-member-host">
            {builderError
              ? <div className="validation bad"><b>RECOVERED COMPONENT ERROR</b><span>{builderError}</span></div>
              : <p>Hosted component surface for <code>{selectedComponent || member.component}</code> is mounted in this body region.</p>}
          </section>,
          footer: <section className="workflow-page-builder-member-status">
            {memberInitClicks[member.id] ? <span>Initialization attempt #{memberInitClicks[member.id]} triggered for {member.id}.</span> : <span>Status: waiting for INIT or next host pass.</span>}
            {memberJsonErrors[member.id] ? <span className="validation bad">{memberJsonErrors[member.id]}</span> : <span className="validation good">Member JSON is valid.</span>}
          </section>,
        };
      } catch (reason) {
        const error = reason instanceof Error ? reason : new Error(String(reason));
        return {
          value: "Component initialization failed",
          detail: error.message || "Unknown initialization error",
          baseClass: "english-workflow-contract-panel workflow-page-builder-member workflow-page-builder-error",
          scrollSize: "420px",
          content: <section>
            <div className="validation bad">
              <b>RECOVERED COMPONENT ERROR</b>
              <span>{error.message || "Unknown component initialization error"}</span>
            </div>
            <div className="operation-abstract-summary">
              <div><span>COMPONENT</span><code>{member.component}</code></div>
              <div><span>MEMBER ID</span><code>{member.id}</code></div>
              <div><span>COLUMN</span><code>{column.id}</code></div>
            </div>
            <pre>{error.stack || error.message}</pre>
          </section>,
        };
      }
    };
    return Object.fromEntries([...components].map((component) => [component, renderMember]));
  }, [
    definition,
    componentDrafts,
    componentOptions,
    memberHeaderCollapsed,
    memberJsonDrafts,
    memberJsonEditorCollapsed,
    memberJsonErrors,
    memberInitClicks,
  ]);
  const memberCount = definition?.layout.columns.reduce((total, column) => total + column.members.length, 0) || 0;
  let hosted: ReactNode | null = null;
  let hostedInitError = "";
  let hostedConstructorMissing = false;
  if (definition && initialized && renderDefinition) {
    try {
      hosted = renderDefinition(definition);
    } catch (reason) {
      const error = reason instanceof Error ? reason : new Error(String(reason));
      hostedInitError = error.stack || error.message;
      hostedConstructorMissing = /constructor not found|is not a function|undefined/i.test(error.message || "");
    }
  }

  return <section className="workflow-page-builder" aria-label="Workflow Page Builder">
    <header className="workflow-page-builder-header">
      <div><span>WORKFLOW PAGE BUILDER</span><h1>Paste JSON → LOAD structure</h1><p>Build any declarative workflow_page without adding hard-coded React layout.</p></div>
      <div>
        <b>{definition?.label || "No valid page"}</b>
        <small>{memberCount} declared members · {definition ? initialized ? "initialized" : "loaded" : "cleared"}</small>
        <button type="button" className="primary" disabled={!definition} onClick={init}>INIT</button>
      </div>
    </header>
    <div className="workflow-page-builder-source">
      <header><label>CURRENT PAGE SPECIFICATION</label><div><button type="button" onClick={clear}>CLEAR</button><button type="button" className="primary" disabled={!source.trim() || !sourceValid} onClick={load}>LOAD</button></div></header>
      <ResourceSourceEditor
        value={source}
        onChange={(next) => {
          setSource(next);
          setError("");
          setMessage("Draft changed. Select LOAD to construct the UI.");
        }}
        onValidityChange={setSourceValid}
        className="workflow-page-source-editor"
        label="Current page specification (MeTTa/JSON/Tree)"
        showEnablement={false}
      />
      <footer>
        <span className={error ? "validation bad" : "validation good"}>{error ? `Load error: ${error} ${message}` : message}</span>
        {initialDefinition && <button type="button" onClick={() => { setSource(initialDefinitionSource); setSourceValid(true); setError(""); setMessage("Filesystem page restored in the editor. Select LOAD to synchronize the declaration."); }}>Restore filesystem page</button>}
      </footer>
    </div>
    <div className="workflow-page-builder-preview">
      {!definition ? <div className="studio-empty">Paste a valid workflow_page JSON document to render the preview.</div> : hostedInitError ? <section className="english-workflow-contract-panel workflow-page-builder-member workflow-page-builder-error">
        <div className="validation bad">
          <b>{hostedConstructorMissing ? "HOSTED PAGE CONSTRUCTOR NOT FOUND" : "HOSTED PAGE INITIALIZATION FAILED"}</b>
          <span>{hostedConstructorMissing ? `Component constructor was not found for renderer ${definition.renderer}.` : `${definition.renderer} could not be initialized.`}</span>
        </div>
        <div className="operation-abstract-summary">
          <div><span>RENDERER</span><code>{definition.renderer}</code></div>
          <div><span>PAGE ID</span><code>{definition.id}</code></div>
        </div>
        {!hostedConstructorMissing && <pre>{hostedInitError}</pre>}
      </section> : hosted ? <HostedDefinitionBoundary definition={definition}>{hosted}</HostedDefinitionBoundary> : <WorkflowPageHost definition={definition} componentRegistry={registry} deferComponentInitialization pageClassName="english-workflow-page workflow-page-builder-rendered" />}
    </div>
  </section>;
}
