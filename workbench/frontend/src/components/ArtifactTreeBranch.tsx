import { createContext, useContext, useEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { accordionPanelClass, ThreeStateAccordionControls, ThreeStateAccordionStripSummary, type AccordionDisplayMode } from "./ThreeStateAccordion";

export type ArtifactTreeCommand = { action: "collapse" | "expand"; revision: number; target?: string } | null;

export const ArtifactTreeCommandContext = createContext<ArtifactTreeCommand>(null);
const ArtifactTreeParentKindContext = createContext<string | null>(null);

function resourceKind(value: unknown): string | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const record = value as Record<string, unknown>;
  const document = record.document && typeof record.document === "object" && !Array.isArray(record.document) ? record.document as Record<string, unknown> : record;
  return typeof document.kind === "string" ? document.kind : null;
}

type ArtifactTreeBranchProps = {
  label: string;
  header: ReactNode;
  children?: ReactNode;
  className?: string;
  childrenClassName?: string;
  style?: CSSProperties;
  searchValue?: unknown;
  branchCommand?: ArtifactTreeCommand;
  initialCollapsed?: boolean;
  displayMode?: AccordionDisplayMode;
  onDisplayModeChange?: (mode: AccordionDisplayMode) => void;
  summaryValue?: string;
};

export function ArtifactTreeBranch({ label, header, children, className = "operation-tree-group", childrenClassName = "operation-tree-children", style, searchValue, branchCommand, initialCollapsed = false, displayMode, onDisplayModeChange, summaryValue }: ArtifactTreeBranchProps) {
  const contextCommand = useContext(ArtifactTreeCommandContext);
  const parentKind = useContext(ArtifactTreeParentKindContext);
  const command = branchCommand === undefined ? contextCommand : branchCommand;
  const [collapsed, setCollapsed] = useState(initialCollapsed);
  const branchRef = useRef<HTMLDivElement>(null);
  const hasChildren = children !== undefined && children !== null;
  const kind = resourceKind(searchValue);
  const role = kind ? `${parentKind === kind ? "child" : "top"}-${kind}` : "other";
  const controlled = displayMode !== undefined && onDisplayModeChange !== undefined;

  useEffect(() => {
    if (!command || controlled) return;
    const disabled = Boolean(branchRef.current?.querySelector(":scope > .artifact-tree-branch-head .resource-disabled"));
    const matches = !command.target || command.target === role
      || (command.target === `unspecialized-${kind}` && !hasChildren)
      || (command.target === "enabled" && !disabled)
      || (command.target === "disabled" && disabled)
      || (command.target === "search" && branchRef.current?.classList.contains("tree-search-match"));
    if (matches) setCollapsed(command.action === "collapse");
  }, [command, controlled, hasChildren, kind, role]);

  const branchClass = controlled ? accordionPanelClass(className, displayMode) : className;
  return <ArtifactTreeParentKindContext.Provider value={kind}>
    <div ref={branchRef} className={`${branchClass} ${controlled ? "workflow-step-accordion" : collapsed ? "branch-collapsed" : "branch-expanded"}`.trim()} style={style} data-tree-search={searchValue === undefined ? undefined : JSON.stringify(searchValue)}>
      {controlled && <ThreeStateAccordionControls label={label} mode={displayMode} onChange={onDisplayModeChange} />}
      {controlled && <ThreeStateAccordionStripSummary title={label} value={summaryValue} onOpen={() => onDisplayModeChange("scroll")} />}
      <div className="artifact-tree-branch-head">
        <div className="artifact-tree-branch-summary">{header}</div>
        {hasChildren && !controlled && <button type="button" className="tree-branch-toggle" title={collapsed ? "Unhide Variants" : "Hide Variants"} aria-label={`${collapsed ? "Unhide" : "Hide"} Variants for ${label}`} aria-expanded={!collapsed} onClick={() => setCollapsed(value => !value)}><span aria-hidden="true">{collapsed ? "›" : "⌄"}</span><b>{collapsed ? "Unhide Variants" : "Hide Variants"}</b></button>}
      </div>
      {hasChildren && (controlled ? displayMode !== "strip" : !collapsed) && <div className={`${childrenClassName} ${controlled ? "three-state-tree-body" : ""}`.trim()}>{children}</div>}
    </div>
  </ArtifactTreeParentKindContext.Provider>;
}
