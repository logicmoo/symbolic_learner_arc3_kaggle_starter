import { useEffect, useMemo, useState, type ReactNode } from "react";
import { ArtifactTreeCommandContext, type ArtifactTreeCommand } from "./ArtifactTreeBranch";
import { RepeatSwitch, TreeViewControls } from "./TreeViewControls";
import { DEFAULT_TREE_VISIBILITY_RULES, type TreeVisibilityRules, useArtifactTreeFilter } from "./useArtifactTreeFilter";
import { CategorizedArtifactNodes } from "./CategorizedArtifactTree";
import { TreePaneResizer } from "./TreePaneResizer";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { MarkdownDocument } from "./MarkdownDocument";
import { ResourceExecutionPlayground } from "./ResourceExecutionPlayground";
import {
  describeOperationDocument,
  OperationDocumentControl,
  type OperationSuperControlRequest,
} from "./OperationDocumentControl";
import {
  builtinSubControls,
  fetchSubControls,
  selectSubControls,
  type SubControlDescriptor,
} from "../lib/subControls";
import "../styles/operation_editor.css";
import "../styles/super_control.css";

export const UNIVERSAL_ARTIFACT_EDITOR_BASELINE = "current-rich-editor";

export type UniversalArtifactTab = {
  key: string;
  kind: string;
  label: string;
  dirty?: boolean;
  subtitle?: string;
};

export type UniversalArtifactBottomPanel = {
  id: string;
  label: string;
  content: ReactNode;
  badge?: string | number;
};

export type UniversalArtifactPageProps = {
  appearance?: "page";
  workspaceId?: string;
  categoryTree?: string;
  eyebrow: string;
  title: string;
  description: string;
  category?: string;
  breadcrumb?: string[];
  headerActions?: ReactNode;
  notice?: ReactNode;
  error?: string | null;
  onDismissError?: () => void;

  /** Rich specification/variant navigator on the left. */
  leftPane: ReactNode;

  /** Persistent multi-document tabs. */
  tabs: UniversalArtifactTab[];
  activeKey: string | null;
  compareKey: string | null;
  onActivate: (key: string) => void;
  onClose: (key: string) => void;

  /** Resource-specific editor body. Operations may render Python/Prolog/MeTTa/LLM panels here. The third arg is the current display view. */
  renderEditor: (key: string, secondary: boolean, view?: "single" | "full") => ReactNode;
  emptyEditor?: ReactNode;

  /** Common inspector extension: dependencies, used-by, coverage, provenance, etc. */
  inspector?: ReactNode;

  /** Optional shared controls such as Preferred Implementation, Representation, or Prompt Alternative. */
  variantControls?: ReactNode;

  /** Documentation, History, Tests, Benchmarks, Diff, Logs, or other dockable panels. */
  bottomPanels?: UniversalArtifactBottomPanel[];
  footer?: ReactNode;

  className?: string;
  treeClassName?: string;
  workspaceClassName?: string;
  tabsClassName?: string;
  panesClassName?: string;

  /** Page-selectable display: "single" shows the active tab as the whole thing; "full" is the multi-tab Super Control. Defaults to "full". */
  initialView?: "single" | "full";
  /** Hide the runtime File⇄Super Control toggle when true. */
  lockView?: boolean;
  /** Omit the left hierarchy navigator column (for filesystem hosts that bring their own browser). */
  hideNavigator?: boolean;
};

export type UniversalArtifactEmbeddedProps = {
  appearance: "embedded";
  control: EmbeddedSuperControlRequest;
  className?: string;
};

export type SuperControlProps = UniversalArtifactPageProps | UniversalArtifactEmbeddedProps;
export type UniversalArtifactEditorProps = SuperControlProps;

type StandardControlId = "file" | "markdown" | "resource" | "runner";
type StandardResource = { kind: string; id: string; label?: string; enabled?: boolean; [key: string]: unknown };
type SuperControlDisplayMode = "tabs" | "stacked" | "single" | "split-v" | "split-h";
type SuperControlTabSet = "all" | "ctx";
export type StandardSuperControlAction = {
  id: string;
  label: string;
  disabled?: boolean;
  onInvoke: () => void;
};
export type StandardSuperControlRequest = {
  kind: "standard";
  workspaceId: string;
  source: string;
  sourceScope: string;
  path: string;
  title: string;
  dirty: boolean;
  secondary: boolean;
  busy: boolean;
  resource: StandardResource | null;
  initialControlId?: StandardControlId;
  onChange: (value: string) => void;
  onSave: () => void;
  saveLabel?: string;
  actions?: StandardSuperControlAction[];
};
type EmbeddedSuperControlRequest = OperationSuperControlRequest | StandardSuperControlRequest;

const OPERATION_DOCUMENT_CONTROL_ID = "operation-document";
const CONTENT_BACKED_CONTROL_IDS = new Set<StandardControlId>([
  "file",
  "markdown",
  "resource",
  "runner",
]);

function hasControlRenderer(control: SubControlDescriptor): boolean {
  return CONTENT_BACKED_CONTROL_IDS.has(control.id as StandardControlId);
}

function uniqueControls(controls: SubControlDescriptor[]): SubControlDescriptor[] {
  const seen = new Set<string>();
  return controls.filter(control => {
    if (seen.has(control.id)) return false;
    seen.add(control.id);
    return true;
  });
}

function parsedJsonObject(source: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(source);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? parsed as Record<string, unknown>
      : null;
  } catch {
    return null;
  }
}

function metadataText(resource: Record<string, unknown>, key: string): string {
  const value = resource[key];
  return typeof value === "string" ? value.trim() : "";
}

function resourceHeader(source: string, fallback: string) {
  const resource = parsedJsonObject(source);
  if (!resource) return { title: fallback, resolved: false };
  const id = metadataText(resource, "id");
  const label = metadataText(resource, "label");
  const discriminator = metadataText(resource, "kind")
    || metadataText(resource, "type")
    || metadataText(resource, "subkind")
    || metadataText(resource, "role")
    || "resource";
  const kind = discriminator.replace(/[_-]+/g, " ").toUpperCase();
  const identity = label
    ? `${label}${id && id !== label ? ` (${id})` : ""}`
    : id || fallback;
  return { title: `${kind} - ${identity}`, resolved: true };
}

function EmbeddedSuperControl({
  control,
  className = "",
}: {
  control: EmbeddedSuperControlRequest;
  className?: string;
}) {
  const isOperation = control.kind === "operation";
  const operationMetadata = isOperation ? describeOperationDocument(control.source, control.path) : null;
  const resource = operationMetadata?.document || (!isOperation ? control.resource : null);
  const fallbackTitle = operationMetadata?.title || (!isOperation ? control.title : control.path);
  const header = resourceHeader(control.source, fallbackTitle);
  const [availableControls, setAvailableControls] = useState<SubControlDescriptor[]>(() => builtinSubControls());
  const [displayMode, setDisplayMode] = useState<SuperControlDisplayMode>("tabs");
  const [tabSet, setTabSet] = useState<SuperControlTabSet>("ctx");
  const [activeControlId, setActiveControlId] = useState(
    control.kind === "operation" ? OPERATION_DOCUMENT_CONTROL_ID : control.initialControlId || "file",
  );
  const [singleControlId, setSingleControlId] = useState<string>("file");
  const [secondaryControlId, setSecondaryControlId] = useState<string>("resource");
  useEffect(() => {
    let cancelled = false;
    void fetchSubControls().then(controls => {
      if (!cancelled) setAvailableControls(controls);
    });
    return () => { cancelled = true; };
  }, []);
  const specialControl = useMemo<SubControlDescriptor | null>(
    () => control.kind === "operation" && operationMetadata
      ? { id: OPERATION_DOCUMENT_CONTROL_ID, label: operationMetadata.tabLabel, source: "operation" }
      : null,
    [control.kind, operationMetadata?.tabLabel],
  );
  const contextualControls = useMemo(
    () => selectSubControls(availableControls.filter(hasControlRenderer), {
      resourceKind: resource?.kind || null,
      capabilities: resource && Array.isArray((resource as Record<string, unknown>).capabilities)
        ? ((resource as Record<string, unknown>).capabilities as unknown[]).filter((value): value is string => typeof value === "string")
        : [],
    }),
    [availableControls, resource],
  );
  const selectedControls = useMemo(
    () => uniqueControls([
      ...(specialControl ? [specialControl] : []),
      ...(tabSet === "all" ? availableControls.filter(hasControlRenderer) : contextualControls),
    ]),
    [availableControls, contextualControls, specialControl, tabSet],
  );
  useEffect(() => {
    if (!selectedControls.length) return;
    const ids = selectedControls.map(entry => entry.id);
    const defaultId = ids.includes("file") ? "file" : ids[0];
    if (!ids.includes(activeControlId)) setActiveControlId(defaultId);
    if (!ids.includes(singleControlId)) setSingleControlId(defaultId);
    if (!ids.includes(secondaryControlId) || secondaryControlId === singleControlId) {
      setSecondaryControlId(ids.find(id => id !== singleControlId) || defaultId);
    }
  }, [activeControlId, secondaryControlId, selectedControls, singleControlId]);
  const sourceEditor = ({
    readOnly = false,
    label = control.path,
  }: {
    readOnly?: boolean;
    label?: string;
  } = {}) => <ResourceSourceEditor
        value={control.source}
        onChange={readOnly ? () => {} : control.onChange}
        contentReadOnly={readOnly}
        showEnablement={false}
        label={label}
        sourcePath={control.path}
        resourceMetadata={resource || undefined}
      />;
  const renderControl = (id: string): ReactNode => {
    switch (id) {
      case OPERATION_DOCUMENT_CONTROL_ID:
        return isOperation
          ? <OperationDocumentControl request={control} />
          : <div className="studio-empty">This operation editor is not available for the current resource.</div>;
      case "file":
      case "resource":
        return sourceEditor();
      case "markdown":
        return <div className="markdown-render operation-editor-scroll">
          <MarkdownDocument content={control.source} onChange={control.onChange} editable />
        </div>;
      case "runner":
        return resource
          ? <ResourceExecutionPlayground workspaceId={control.workspaceId} resource={resource} />
          : <div className="studio-empty">Fix the resource source before opening the runner.</div>;
      default: {
        return null;
      }
    }
  };
  const controlOptions = selectedControls.map(entry =>
    <option key={entry.id} value={entry.id}>{entry.label}</option>,
  );
  const singleBody = displayMode === "single"
    ? <div className="super-control-body super-control-single">{renderControl(singleControlId)}</div>
    : null;
  const splitBody = displayMode === "split-v" || displayMode === "split-h"
    ? <div className={`super-control-body super-control-split ${displayMode}`}>
        <div className="super-control-pane" data-pane="primary">{renderControl(singleControlId)}</div>
        <div className="super-control-pane" data-pane="secondary">{renderControl(secondaryControlId)}</div>
      </div>
    : null;
  const stackedBody = displayMode === "stacked"
    ? <div className="super-control-body super-control-stack">
        {selectedControls.map(entry => <section className="super-control-stack-section" key={entry.id}>
          <h3>{entry.label}</h3>
          <div className="super-control-stack-section-body">{renderControl(entry.id)}</div>
        </section>)}
      </div>
    : null;

  return <section
    className={`super-control super-control-embedded ${control.secondary ? "secondary" : "primary"} ${className}`.trim()}
    data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}
    data-appearance="embedded"
  >
    <div className="operation-editor-toolbar">
      <div>
        <span>SUPER CONTROL{control.dirty ? <i className="super-control-state"> · UNSAVED</i> : null}</span>
        <h2>{header.title}</h2>
        <small>{control.sourceScope} · {control.path}{!header.resolved ? " · identity unresolved" : ""}</small>
      </div>
      <div className="operation-editor-actions">
        {control.kind === "operation" && operationMetadata?.document && control.onToggleEnabled && <button
          className={operationMetadata.document.enabled === false ? "enable-resource" : "disable-resource"}
          onClick={control.onToggleEnabled}
        >
          {operationMetadata.document.enabled === false ? "Enable Resource" : "Disable Resource"}
        </button>}
        <div className="super-control-tab-set" role="group" aria-label="Super Control tab set">
          <b>TABS</b>
          <span className="super-control-tab-set-buttons">
            <button type="button" className={tabSet === "all" ? "active" : ""} aria-pressed={tabSet === "all"} onClick={() => setTabSet("all")}>ALL</button>
            <button type="button" className={tabSet === "ctx" ? "active" : ""} aria-pressed={tabSet === "ctx"} onClick={() => setTabSet("ctx")}>CTX</button>
          </span>
        </div>
        <label className="super-control-mode-switcher">
          <span>DISPLAY</span>
          <select aria-label="Super Control display mode" value={displayMode} onChange={event => setDisplayMode(event.target.value as SuperControlDisplayMode)}>
            <option value="tabs">Tabs</option>
            <option value="stacked">Stacked</option>
            <option value="single">Single</option>
            <option value="split-v">SplitV</option>
            <option value="split-h">SplitH</option>
          </select>
        </label>
        {(displayMode === "single" || displayMode === "split-v" || displayMode === "split-h") && <label className="super-control-pane-selector">
          <span>{displayMode === "single" ? "TAB" : displayMode === "split-v" ? "LEFT" : "TOP"}</span>
          <select aria-label="Primary Super Control tab" value={singleControlId} onChange={event => setSingleControlId(event.target.value)}>{controlOptions}</select>
        </label>}
        {(displayMode === "split-v" || displayMode === "split-h") && <label className="super-control-pane-selector">
          <span>{displayMode === "split-v" ? "RIGHT" : "BOTTOM"}</span>
          <select aria-label="Secondary Super Control tab" value={secondaryControlId} onChange={event => setSecondaryControlId(event.target.value)}>{controlOptions}</select>
        </label>}
        <button className="primary" onClick={control.onSave} disabled={control.busy || !resource}>{control.kind === "standard" ? control.saveLabel || "Save" : "Save"}</button>
        {control.kind === "standard" && control.actions?.map(action => <button
          key={action.id}
          disabled={action.disabled}
          onClick={action.onInvoke}
        >{action.label}</button>)}
      </div>
    </div>
    {displayMode === "tabs" && <nav className="super-control-tabs" aria-label="Super Control editors" role="tablist">
      <span className="super-control-tabs-label">EDITORS</span>
      {selectedControls.map(entry => <button
        key={entry.id}
        role="tab"
        aria-selected={activeControlId === entry.id}
        className={activeControlId === entry.id ? "active" : ""}
        onClick={() => setActiveControlId(entry.id)}
      >{entry.label}{entry.id === OPERATION_DOCUMENT_CONTROL_ID && control.dirty ? <i className="dirty">●</i> : null}</button>)}
    </nav>}
    {displayMode === "tabs" && <div className="super-control-body super-control-tabbed">{renderControl(activeControlId)}</div>}
    {stackedBody}
    {singleBody}
    {splitBody}
  </section>;
}

/**
 * Universal Artifact Editor.
 *
 * The current active rich Operations experience is the feature baseline:
 * - semantic specification -> concrete variants on the left
 * - persistent, closeable, dirty-aware editor tabs
 * - side-by-side comparison
 * - preferred/default variant controls
 * - rich type-specific editors rather than a lowest-common-denominator JSON form
 * - common inspector and dock slots
 *
 * Artifact-family adapters add capabilities; they must not remove baseline behavior.
 */
export function SuperControl(props: SuperControlProps) {
  if (props.appearance === "embedded") {
    return <EmbeddedSuperControl control={props.control} className={props.className} />;
  }

  const {
  workspaceId,
  categoryTree,
  eyebrow,
  title,
  description,
  category,
  breadcrumb,
  headerActions,
  notice,
  error,
  onDismissError,
  leftPane,
  tabs,
  activeKey,
  compareKey,
  onActivate,
  onClose,
  renderEditor,
  emptyEditor,
  inspector,
  variantControls,
  bottomPanels = [],
  footer,
  className = "",
  treeClassName = "operation-tree-pane",
  workspaceClassName = "operation-editor-workspace",
  tabsClassName = "operation-document-tabs",
  panesClassName = "operation-editor-panes",
  initialView = "full",
  lockView = false,
  hideNavigator = false,
  } = props;
  const activeTab = tabs.find(tab => tab.key === activeKey) || null;
  const compareTab = tabs.find(tab => tab.key === compareKey) || null;
  const [view, setView] = useState<"single" | "full">(initialView);
  const trail = breadcrumb?.length
    ? breadcrumb
    : [category || title, activeTab?.label || "Select artifact"];
  const [bottomPanelId, setBottomPanelId] = useState<string | null>(bottomPanels[0]?.id || null);
  const [navigatorCollapsed, setNavigatorCollapsed] = useState(false);
  const [viewControlsOpen, setViewControlsOpen] = useState(false);
  const [treeCommand, setTreeCommand] = useState<ArtifactTreeCommand>(null);
  const [categoryCommand, setCategoryCommand] = useState<ArtifactTreeCommand>(null);
  const [visibilityRules, setVisibilityRules] = useState<TreeVisibilityRules>(DEFAULT_TREE_VISIBILITY_RULES);
  const { treeRef, treeFilter, setTreeFilter, showParents, setShowParents, treeKinds } = useArtifactTreeFilter(visibilityRules);
  const commandTree = (action: "collapse" | "expand", target?: string) => setTreeCommand(current => ({ action, target, revision: (current?.revision || 0) + 1 }));
  const commandCategories = (action: "collapse" | "expand") => setCategoryCommand(current => ({ action, revision: (current?.revision || 0) + 1 }));
  const commandBranches = (action: "collapse" | "expand", target: string) => {
    if (target === "all") { commandCategories(action); commandTree(action); }
    else if (target === "categories") commandCategories(action);
    else commandTree(action, target);
  };
  const updateVisibilityRules = (next: TreeVisibilityRules) => {
    setVisibilityRules(next);
  };
  const activeBottomPanel = useMemo(
    () => bottomPanels.find(panel => panel.id === bottomPanelId) || bottomPanels[0] || null,
    [bottomPanels, bottomPanelId],
  );

  if (view === "single") {
    return <section className={`super-control uae-single ${className}`.trim()} data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}>
      <div className="uae-single-bar">
        <div className="uae-single-heading"><span>{eyebrow}</span><b>{activeTab?.label || title}</b></div>
        <div className="uae-single-actions">{headerActions}{!lockView && <button type="button" className="uae-view-toggle" onClick={() => setView("full")} title="Show the full Super Control with all tabs">▣ Super Control</button>}</div>
      </div>
      {notice}
      {error && <div className="backend-error"><b>{title}</b><span>{error}</span>{onDismissError && <button onClick={onDismissError}>×</button>}</div>}
      <div className="uae-single-body">{activeKey ? renderEditor(activeKey, false, "single") : (emptyEditor || <div className="studio-empty">Select a specification or variant.</div>)}</div>
    </section>;
  }

  return <section
    className={`resource-view operation-hierarchy-page generic-hierarchy-editor super-control ${className}`.trim()}
    data-editor-baseline={UNIVERSAL_ARTIFACT_EDITOR_BASELINE}
  >
    <div className="artifact-breadcrumb" aria-label="Artifact breadcrumb">
      {trail.map((item,index)=><span key={`${item}:${index}`}><b>{item}</b>{index<trail.length-1&&<i>›</i>}</span>)}
    </div>

    <div className="resource-heading artifact-editor-heading">
      <div><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>
      {(headerActions || !lockView) && <div className="studio-actions">{!lockView && <button type="button" className="uae-view-toggle" onClick={() => setView("single")} title="Collapse to the single editable file view">⛶ Editable File</button>}{headerActions}</div>}
    </div>

    {notice}
    {error && <div className="backend-error"><b>{title}</b><span>{error}</span>{onDismissError && <button onClick={onDismissError}>×</button>}</div>}

    <div className="artifact-common-inspector">
      <div><span>CATEGORY</span><b>{category || eyebrow}</b></div>
      <div><span>ARTIFACT</span><b>{activeTab?.label || "—"}</b></div>
      <div><span>TYPE / VARIANT</span><b>{activeTab?.kind || "—"}</b></div>
      <div><span>STATE</span><b>{activeTab?.dirty ? "unsaved" : activeTab ? "loaded" : "idle"}</b></div>
      <div><span>OPEN</span><b>{tabs.length}</b></div>
      <div><span>COMPARE</span><b>{compareTab?.label || "off"}</b></div>
      {variantControls && <div className="artifact-inspector-extension artifact-variant-controls">{variantControls}</div>}
      {inspector && <div className="artifact-inspector-extension">{inspector}</div>}
    </div>

    <div className={`operation-hierarchy-layout artifact-editor-body ${hideNavigator?"navigator-hidden":navigatorCollapsed?"navigator-collapsed":"navigator-expanded"}`}>
      {!hideNavigator && <div className={`${treeClassName} artifact-navigator`.trim()}>
        <div className="artifact-navigator-toolbar">
          <span>HIERARCHY</span>
          <div className="artifact-navigator-actions">
            <label className="artifact-tree-filter"><span>Filter tree</span><input type="search" value={treeFilter} onChange={event=>{const value=event.target.value;setTreeFilter(value);if(value.trim())commandTree("expand")}} placeholder="Filter tree…" /></label>
            <div className="tree-repeat-permanent"><RepeatSwitch value={visibilityRules.repeats} onChange={repeats=>updateVisibilityRules({...visibilityRules,repeats})} /></div>
            <button type="button" aria-label="Expand All" onClick={()=>{commandCategories("expand");commandTree("expand")}}><b>Expand All</b></button>
            <button type="button" aria-label="Collapse All" onClick={()=>{commandTree("collapse");commandCategories("collapse")}}><b>Collapse All</b></button>
            <button type="button" aria-label="Tree View Controls" aria-expanded={viewControlsOpen} aria-pressed={viewControlsOpen} onClick={()=>setViewControlsOpen(value=>!value)}><b>{viewControlsOpen ? "Hide View" : "Show View"}</b></button>
            <button type="button" aria-label={navigatorCollapsed?"Expand hierarchy":"Collapse hierarchy"} aria-expanded={!navigatorCollapsed} onClick={()=>setNavigatorCollapsed(value=>!value)}>{navigatorCollapsed?"›":"‹"}<b>{navigatorCollapsed?"":"Pane"}</b></button>
          </div>
        </div>
        {viewControlsOpen && <TreeViewControls kinds={treeKinds} rules={visibilityRules} onChange={updateVisibilityRules} showParents={showParents} onShowParentsChange={setShowParents} onBranchAction={commandBranches} />}
        <ArtifactTreeCommandContext.Provider value={treeCommand}><div className="artifact-navigator-content" ref={treeRef}><CategorizedArtifactNodes onlyCategories={false} categoryCommand={categoryCommand} workspaceId={workspaceId} categoryTree={categoryTree}>{leftPane}</CategorizedArtifactNodes></div></ArtifactTreeCommandContext.Provider>
      </div>}
      <div className={workspaceClassName}>
        <TreePaneResizer />
        <div className={tabsClassName}>
          {tabs.map(tab => <div className={`operation-document-tab ${tab.key===activeKey?"active":""}`} key={tab.key}>
            <button onClick={()=>onActivate(tab.key)} title={tab.subtitle || tab.label}>
              <span>{tab.kind}</span><b>{tab.label}</b>{tab.key===activeKey&&compareKey?<em className="artifact-pane-side left">LEFT</em>:null}{tab.key===compareKey?<em className="artifact-pane-side right">RIGHT</em>:null}{tab.dirty&&<i>●</i>}
            </button>
            <button className="close" onClick={()=>onClose(tab.key)}>×</button>
          </div>)}
        </div>
        <div className={`${panesClassName} ${compareKey?"split":"single"}`}>
          {activeKey ? renderEditor(activeKey,false,"full") : (emptyEditor || <div className="studio-empty">Select a specification or variant.</div>)}
          {compareKey ? renderEditor(compareKey,true,"full") : null}
        </div>
      </div>
    </div>

    {bottomPanels.length > 0 && <section className="artifact-bottom-dock">
      <nav className="artifact-bottom-tabs">
        {bottomPanels.map(panel=><button
          key={panel.id}
          className={activeBottomPanel?.id===panel.id?"active":""}
          onClick={()=>setBottomPanelId(panel.id)}
        >{panel.label}{panel.badge!==undefined&&<span>{panel.badge}</span>}</button>)}
      </nav>
      <div className="artifact-bottom-content">{activeBottomPanel?.content}</div>
    </section>}

    {footer}
  </section>;
}

/** Compatibility export for incrementally migrated artifact-family adapters. */
export const UniversalArtifactEditor = SuperControl;
