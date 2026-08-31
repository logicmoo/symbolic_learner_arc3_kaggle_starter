import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useCollapsingHeaderWheel } from "../lib/collapsingHeaderWheel";
import { ArtifactTreeCommandContext, type ArtifactTreeCommand } from "./ArtifactTreeBranch";
import { RepeatSwitch, TreeViewControls } from "./TreeViewControls";
import { DEFAULT_TREE_VISIBILITY_RULES, type TreeVisibilityRules, useArtifactTreeFilter } from "./useArtifactTreeFilter";
import { CategorizedArtifactNodes } from "./CategorizedArtifactTree";
import { TreePaneResizer } from "./TreePaneResizer";
import { ResourceSourceEditor } from "./ResourceSourceEditor";
import { ResourceFieldsEditor, resourceImplementedIds } from "./ResourceFieldsEditor";
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
  relatedResources?: StandardResource[];
  initialControlId?: StandardControlId;
  onChange: (value: string) => void;
  onSave: () => void;
  onCreateSpecialization?: () => void;
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

// Every mounted Super Control mirrors its active editor tab through `tab`
// URL search parameters: clicking a tab records it (replaceState, so history
// entries are not spammed) and notifies every other mounted instance, while
// back/forward restores whatever tabs the entry was on.
//
// Addressing: instances are ordered by mount order and addressed by their
// distance from the LAST Super Control on the page (0 = last, 1 = one before
// it, ...) or by the file name they edit.
//   tab=Markdown            -> every mounted instance
//   tab0=Markdown           -> the last instance on the page
//   tab2=File               -> the third-from-last instance
//   tab=README.md:Markdown  -> instances editing README.md (name address)
//   tab=0:Markdown          -> value form of the ordinal address
// Parameters may repeat; for one instance the last matching directive wins.
const TAB_URL_PARAM = "tab";
const TAB_SYNC_EVENT = "workbench:super-control-tab";

type SuperControlRegistryEntry = { token: symbol; notify: () => void };
const superControlRegistry: SuperControlRegistryEntry[] = [];

function notifySuperControlRegistry() {
  for (const entry of [...superControlRegistry]) entry.notify();
}

function registerSuperControl(entry: SuperControlRegistryEntry): () => void {
  superControlRegistry.push(entry);
  notifySuperControlRegistry();
  return () => {
    const index = superControlRegistry.indexOf(entry);
    if (index >= 0) superControlRegistry.splice(index, 1);
    notifySuperControlRegistry();
  };
}

/** Distance from the last mounted instance: 0 = last on the page. */
function superControlReverseOrdinal(token: symbol): number {
  const index = superControlRegistry.findIndex(entry => entry.token === token);
  return index < 0 ? -1 : superControlRegistry.length - 1 - index;
}

/** Case-insensitive names an instance answers to: file name with and without extension. */
function addressNamesFor(path: string): string[] {
  const basename = (path || "").replace(/\\/g, "/").split("/").at(-1) || "";
  const bare = basename.replace(/\.[^.]+$/, "");
  return [...new Set([basename, bare].map(value => value.trim().toLowerCase()).filter(Boolean))];
}

type TabDirective = { address: string | null; tab: string };

function parseTabDirective(key: string, raw: string): TabDirective | null {
  const value = raw.trim();
  const keyMatch = /^tab(\d*)$/i.exec(key.trim());
  if (!keyMatch || !value) return null;
  if (keyMatch[1]) return { address: keyMatch[1], tab: value.toLowerCase() };
  const named = /^([^:]+):(.+)$/.exec(value);
  if (named) return { address: named[1].trim().toLowerCase(), tab: named[2].trim().toLowerCase() };
  const prefixed = /^(\d+)(.*\D.*)$/.exec(value);
  return prefixed
    ? { address: prefixed[1], tab: prefixed[2].trim().toLowerCase() }
    : { address: null, tab: value.toLowerCase() };
}

function tabDirectivesFromLocation(): TabDirective[] {
  const directives: TabDirective[] = [];
  for (const [key, raw] of new URLSearchParams(window.location.search)) {
    const directive = parseTabDirective(key, raw);
    if (directive) directives.push(directive);
  }
  return directives;
}

function directiveAddressesInstance(address: string | null, reverseOrdinal: number, names: string[]): boolean {
  if (address === null) return true;
  if (/^\d+$/.test(address)) return reverseOrdinal >= 0 && Number(address) === reverseOrdinal;
  return names.includes(address);
}

function matchControlId(controls: SubControlDescriptor[], wanted: string): string | null {
  if (!wanted) return null;
  const match = controls.find(entry => entry.id.toLowerCase() === wanted)
    || controls.find(entry => entry.label.trim().toLowerCase() === wanted);
  return match ? match.id : null;
}

function wantedTabFor(reverseOrdinal: number, names: string[], controls: SubControlDescriptor[]): string | null {
  let wanted: string | null = null;
  for (const directive of tabDirectivesFromLocation()) {
    if (!directiveAddressesInstance(directive.address, reverseOrdinal, names)) continue;
    const id = matchControlId(controls, directive.tab);
    if (id) wanted = id;
  }
  return wanted;
}

function recordTabInLocation(token: symbol, names: string[], id: string) {
  const url = new URL(window.location.href);
  const reverseOrdinal = superControlReverseOrdinal(token);
  const single = superControlRegistry.length <= 1;
  // Keep directives addressed to other instances; drop plain (all-instance)
  // directives and anything addressing this instance, which this click
  // supersedes. With a single mounted instance collapse to the plain form.
  const keptNumbered: Array<[string, string]> = [];
  const keptValues: string[] = [];
  for (const [key, raw] of [...url.searchParams.entries()]) {
    const directive = parseTabDirective(key, raw);
    if (!directive) continue;
    if (single || directive.address === null) continue;
    if (directiveAddressesInstance(directive.address, reverseOrdinal, names)) continue;
    if (/^tab\d+$/i.test(key.trim())) keptNumbered.push([key.trim().toLowerCase(), raw]);
    else keptValues.push(raw.trim());
  }
  for (const key of [...new Set([...url.searchParams.keys()])]) {
    if (/^tab\d*$/i.test(key.trim())) url.searchParams.delete(key);
  }
  for (const [key, value] of keptNumbered) url.searchParams.set(key, value);
  for (const value of keptValues) url.searchParams.append(TAB_URL_PARAM, value);
  if (single) url.searchParams.set(TAB_URL_PARAM, id);
  else if (reverseOrdinal >= 0) url.searchParams.set(`tab${reverseOrdinal}`, id);
  else url.searchParams.append(TAB_URL_PARAM, id);
  window.history.replaceState(window.history.state, "", url);
  window.dispatchEvent(new Event(TAB_SYNC_EVENT));
}

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
  const resource = parsedJsonObject(control.source)
    || (operationMetadata?.document ? { ...operationMetadata.document } : null)
    || (!isOperation && control.resource ? { ...control.resource } : null);
  const runnableResource = resource
    && typeof resource.kind === "string"
    && typeof resource.id === "string"
    ? { ...resource, kind: resource.kind, id: resource.id }
    : null;
  const fallbackTitle = operationMetadata?.title || (!isOperation ? control.title : control.path);
  const header = resourceHeader(control.source, fallbackTitle);
  const [availableControls, setAvailableControls] = useState<SubControlDescriptor[]>(() => builtinSubControls());
  const [displayMode, setDisplayMode] = useState<SuperControlDisplayMode>("tabs");
  const [tabSet, setTabSet] = useState<SuperControlTabSet>("ctx");
  const registrationToken = useMemo(() => Symbol("super-control"), []);
  const addressNames = useMemo(() => addressNamesFor(control.path), [control.path]);
  const [registryVersion, setRegistryVersion] = useState(0);
  useEffect(
    () => registerSuperControl({ token: registrationToken, notify: () => setRegistryVersion(version => version + 1) }),
    [registrationToken],
  );
  const reverseOrdinal = superControlReverseOrdinal(registrationToken);
  const [activeControlId, setActiveControlId] = useState(() =>
    wantedTabFor(-1, addressNamesFor(control.path), builtinSubControls())
    || (control.kind === "operation" ? OPERATION_DOCUMENT_CONTROL_ID : control.initialControlId || "file"),
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
      resourceKind: typeof resource?.kind === "string" ? resource.kind : null,
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
  useEffect(() => {
    const apply = () => {
      const wanted = wantedTabFor(superControlReverseOrdinal(registrationToken), addressNames, selectedControls);
      if (!wanted) return;
      setActiveControlId(current => (current === wanted ? current : wanted));
      setSingleControlId(current => (current === wanted ? current : wanted));
    };
    apply();
    window.addEventListener("popstate", apply);
    window.addEventListener(TAB_SYNC_EVENT, apply);
    return () => {
      window.removeEventListener("popstate", apply);
      window.removeEventListener(TAB_SYNC_EVENT, apply);
    };
  }, [selectedControls, addressNames, registrationToken, registryVersion]);
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
  const inheritedImplementation = control.kind === "operation" ? control.implementedOperation : null;
  const implementedIds = resource
    ? resourceImplementedIds(resource).length > 0
      ? resourceImplementedIds(resource)
      : inheritedImplementation?.id
        ? [inheritedImplementation.id]
        : []
    : [];
  const resourceHref = (id: string) => {
    const params = new URLSearchParams(window.location.search);
    params.set("resource", id);
    return `?${params.toString()}`;
  };
  const resourceAndInheritance = resource
    ? <div className="operation-editor-scroll super-control-resource-inheritance">
        <ResourceFieldsEditor
          resource={resource}
          relatedResources={control.relatedResources}
          sourceScope={control.sourceScope}
          onChange={control.onChange}
          resourceHref={resourceHref}
          onCreateSpecialization={control.onCreateSpecialization}
        />
        <section className="super-control-inheritance-section">
          <div className="llm-subhead">
            <div>
              <span>INHERITANCE</span>
              <b>{implementedIds.length > 0 ? "Implemented resources and resolved source" : "Family root resource"}</b>
            </div>
          </div>
          {implementedIds.length > 0
            ? <div className="super-control-parent-links">
                {implementedIds.map(id => <a key={id} href={resourceHref(id)}>Edit implemented resource · {id}</a>)}
              </div>
            : <div className="studio-empty super-control-no-parent">This resource does not implement another resource.</div>}
          {inheritedImplementation && <ResourceSourceEditor
            value={JSON.stringify(inheritedImplementation, null, 2)}
            onChange={() => {}}
            contentReadOnly
            showEnablement={false}
            label={`Resolved implementation · ${inheritedImplementation.label || inheritedImplementation.id}`}
            resourceMetadata={inheritedImplementation}
          />}
        </section>
        <section className="super-control-resource-source">
          {sourceEditor({ label: "Resource source" })}
        </section>
      </div>
    : <div className="studio-empty">Fix the resource source before editing its fields or inheritance.</div>;
  const renderControl = (id: string): ReactNode => {
    switch (id) {
      case OPERATION_DOCUMENT_CONTROL_ID:
        return isOperation
          ? <OperationDocumentControl request={control} />
          : <div className="studio-empty">This operation editor is not available for the current resource.</div>;
      case "file":
        return sourceEditor();
      case "resource":
        return resourceAndInheritance;
      case "markdown":
        return <div className="markdown-render operation-editor-scroll">
          <MarkdownDocument content={control.source} onChange={control.onChange} editable />
        </div>;
      case "runner":
        return runnableResource
          ? <ResourceExecutionPlayground workspaceId={control.workspaceId} resource={runnableResource} />
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
        <span>SUPER CONTROL{reverseOrdinal >= 0 ? <i
          className="super-control-state"
          title={`Addressable in the URL as tab${reverseOrdinal}=<TabName>${addressNames[0] ? ` or tab=${addressNames[0]}:<TabName>` : ""}; plain tab=<TabName> targets every Super Control.`}
        > · #{reverseOrdinal}</i> : null}{control.dirty ? <i className="super-control-state"> · UNSAVED</i> : null}</span>
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
          <select aria-label="Primary Super Control tab" value={singleControlId} onChange={event => { setSingleControlId(event.target.value); recordTabInLocation(registrationToken, addressNames, event.target.value); }}>{controlOptions}</select>
        </label>}
        {(displayMode === "split-v" || displayMode === "split-h") && <label className="super-control-pane-selector">
          <span>{displayMode === "split-v" ? "RIGHT" : "BOTTOM"}</span>
          <select aria-label="Secondary Super Control tab" value={secondaryControlId} onChange={event => setSecondaryControlId(event.target.value)}>{controlOptions}</select>
        </label>}
        <button className="primary" onClick={control.onSave} disabled={control.busy || (control.kind === "operation" && !resource)}>{control.kind === "standard" ? control.saveLabel || "Save" : "Save"}</button>
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
        onClick={() => { setActiveControlId(entry.id); recordTabInLocation(registrationToken, addressNames, entry.id); }}
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
  const pageRootRef = useCollapsingHeaderWheel();
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
    ref={pageRootRef}
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
      {!hideNavigator && <div className={`${treeClassName} artifact-navigator${viewControlsOpen ? " view-controls-open" : ""}`.trim()}>
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
