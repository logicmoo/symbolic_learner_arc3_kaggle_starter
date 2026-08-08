import { createContext, useContext, useEffect, useState, type CSSProperties, type ReactNode } from "react";

export type ArtifactTreeCommand = { action: "collapse" | "expand"; revision: number } | null;

export const ArtifactTreeCommandContext = createContext<ArtifactTreeCommand>(null);

export function ArtifactTreeBranch({ label, header, children, className = "operation-tree-group", childrenClassName = "operation-tree-children", style, searchValue, branchCommand }: { label: string; header: ReactNode; children?: ReactNode; className?: string; childrenClassName?: string; style?: CSSProperties; searchValue?: unknown; branchCommand?: ArtifactTreeCommand }) {
  const contextCommand = useContext(ArtifactTreeCommandContext);
  const command = branchCommand === undefined ? contextCommand : branchCommand;
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => { if (command) setCollapsed(command.action === "collapse"); }, [command]);
  const hasChildren = children !== undefined && children !== null;
  return <div className={`${className} ${collapsed ? "branch-collapsed" : "branch-expanded"}`.trim()} style={style} data-tree-search={searchValue === undefined ? undefined : JSON.stringify(searchValue)}>
    <div className="artifact-tree-branch-head"><div className="artifact-tree-branch-summary">{header}</div>{hasChildren && <button type="button" className="tree-branch-toggle" title={collapsed ? "Unhide Variants" : "Hide Variants"} aria-label={`${collapsed ? "Unhide" : "Hide"} Variants for ${label}`} aria-expanded={!collapsed} onClick={() => setCollapsed(value => !value)}><span aria-hidden="true">{collapsed ? "›" : "⌄"}</span><b>{collapsed ? "Unhide Variants" : "Hide Variants"}</b></button>}</div>
    {hasChildren && <div className={childrenClassName}>{children}</div>}
  </div>;
}
