import { useState } from "react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import type { TreeRepeatMode, TreeVisibilityRule, TreeVisibilityRules } from "./useArtifactTreeFilter";

function title(value: string) { return value.replace(/[_-]+/g, " ").replace(/\b\w/g, letter => letter.toUpperCase()); }
function plural(value: string) { return value.endsWith("s") ? value : `${value}s`; }

function ThreePositionSwitch({ label, value, onChange, onExpand, onCollapse }: { label: string; value: TreeVisibilityRule; onChange: (value: TreeVisibilityRule) => void; onExpand?: () => void; onCollapse?: () => void }) {
  return <div className="tree-rule-row">
    <span>{label}</span>
    {onExpand && onCollapse && <div className="tree-branch-actions"><button type="button" onClick={onExpand}>Expand</button><button type="button" onClick={onCollapse}>Collapse</button></div>}
    <div className="tree-rule-switch" role="radiogroup" aria-label={`${label} visibility`}>
      {(["show", "unspecified", "hide"] as TreeVisibilityRule[]).map(option => <button key={option} type="button" role="radio" aria-checked={value === option} className={value === option ? "active" : ""} onClick={() => onChange(option)}>{option === "unspecified" ? "Undef" : title(option)}</button>)}
    </div>
  </div>;
}

export function RepeatSwitch({ value, onChange }: { value: TreeRepeatMode; onChange: (value: TreeRepeatMode) => void }) {
  return <div className="tree-rule-row"><span>Repeated</span><div className="tree-rule-switch" role="radiogroup" aria-label="Repeated resources">
    {(["first", "all", "last"] as TreeRepeatMode[]).map(option => <button key={option} type="button" role="radio" aria-checked={value === option} className={value === option ? "active" : ""} onClick={() => onChange(option)}>{title(option)}</button>)}
  </div></div>;
}

export function TreeViewControls({ kinds, rules, onChange, showParents, onShowParentsChange, onBranchAction, relationshipModesEnabled = false, filterValue = "", onFilterChange, onExpandAll, onCollapseAll }: { kinds: string[]; rules: TreeVisibilityRules; onChange: (rules: TreeVisibilityRules) => void; showParents: boolean; onShowParentsChange: (value: boolean) => void; onBranchAction: (action: "expand" | "collapse", target: string) => void; relationshipModesEnabled?: boolean; filterValue?: string; onFilterChange?: (value: string) => void; onExpandAll?: () => void; onCollapseAll?: () => void }) {
  const [collapsed, setCollapsed] = useState(false);
  const [height, setHeight] = useState<number | null>(null);
  const relationshipLabel = rules.relationshipMode === "implementation" ? "Implements ↔ Implemented By" : rules.relationshipMode === "inheritance" ? "Inherits From ↔ Inherited By" : "Depends On ↔ Depended On By";
  const setRule = (key: "search" | "enabled" | "disabled" | "categories", value: TreeVisibilityRule) => onChange({ ...rules, [key]: value });
  const setRole = (key: string, value: TreeVisibilityRule) => onChange({ ...rules, roles: { ...rules.roles, [key]: value } });
  const kindLabels = kinds.map(title);
  const roleKeys = [...kinds.flatMap(kind => [`top-${kind}`, `child-${kind}`, `childless-${kind}`]), "other"];
  const allValues = [rules.search, rules.enabled, rules.disabled, rules.categories, ...roleKeys.map(key => rules.roles[key] || "unspecified")];
  const masterValue: TreeVisibilityRule = allValues.every(value => value === allValues[0]) ? allValues[0] : "unspecified";
  const setAll = (value: TreeVisibilityRule) => onChange({ ...rules, search: value, enabled: value, disabled: value, categories: value, roles: Object.fromEntries(roleKeys.map(key => [key, value])) });
  const reset = () => onChange({ search: "unspecified", enabled: "unspecified", disabled: "unspecified", categories: "unspecified", repeats: "all", relationshipMode: rules.relationshipMode, roles: {} });
  const card = (key: string, control: React.ReactNode, className = "") => <div className={`tree-rule-group ${className}`} key={key}>{control}</div>;
  const beginResize = (event: ReactPointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const panel = event.currentTarget.closest<HTMLElement>(".tree-view-controls");
    const navigator = panel?.parentElement;
    if (!panel || !navigator) return;
    const startY = event.clientY;
    const startHeight = panel.getBoundingClientRect().height;
    const maximum = Math.max(120, navigator.getBoundingClientRect().height - 150);
    const move = (pointer: PointerEvent) => setHeight(Math.max(75, Math.min(maximum, startHeight + pointer.clientY - startY)));
    const stop = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", stop);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop, { once: true });
  };

  return <section className={`tree-view-controls${collapsed ? " is-collapsed" : ""}`} aria-label="Tree View Controls" style={height && !collapsed ? {"--tree-filter-height": `${height}px`} as CSSProperties : undefined}>
    <header>
      <div><b>TREE FILTERS</b><span>{relationshipModesEnabled ? `${relationshipLabel}. ` : ""}Search overrides all; otherwise Hide overrides Show.</span></div>
      <div className="tree-view-controls-actions">
        <button type="button" aria-expanded={!collapsed} onClick={() => setCollapsed(value => !value)}>{collapsed ? "▾ Expand" : "▴ Collapse"}</button>
        <button type="button" onClick={reset}>Reset</button>
      </div>
    </header>
    {!collapsed && <div className="tree-control-band">
      <div className="tree-filter-toolbar">
        <label><span>FILTER TREE</span><input type="search" value={filterValue} onChange={event => onFilterChange?.(event.target.value)} placeholder="Filter tree..." /></label>
        <RepeatSwitch value={rules.repeats} onChange={repeats => onChange({...rules, repeats})} />
        <button type="button" onClick={onExpandAll}>Expand All</button>
        <button type="button" onClick={onCollapseAll}>Collapse All</button>
      </div>
      <div className="tree-rule-group tree-rule-search"><ThreePositionSwitch label="Search" value={rules.search} onChange={value => setRule("search", value)} onExpand={() => onBranchAction("expand", "search")} onCollapse={() => onBranchAction("collapse", "search")} /><button type="button" className={`tree-binary-switch ${showParents ? "active" : ""}`} role="switch" aria-checked={showParents} onClick={() => onShowParentsChange(!showParents)}><i />Parents</button></div>
      {card("all", <ThreePositionSwitch label="All" value={masterValue} onChange={setAll} onExpand={() => onBranchAction("expand", "all")} onCollapse={() => onBranchAction("collapse", "all")} />, "tree-rule-master")}
      {card("enabled", <ThreePositionSwitch label="Enabled" value={rules.enabled} onChange={value => setRule("enabled", value)} onExpand={() => onBranchAction("expand", "enabled")} onCollapse={() => onBranchAction("collapse", "enabled")} />)}
      {card("disabled", <ThreePositionSwitch label="Disabled" value={rules.disabled} onChange={value => setRule("disabled", value)} onExpand={() => onBranchAction("expand", "disabled")} onCollapse={() => onBranchAction("collapse", "disabled")} />)}
      {card("categories", <ThreePositionSwitch label="Categories" value={rules.categories} onChange={value => setRule("categories", value)} onExpand={() => onBranchAction("expand", "categories")} onCollapse={() => onBranchAction("collapse", "categories")} />)}
      {card("other", <ThreePositionSwitch label={`Non-${kindLabels.join("/") || "Typed"}`} value={rules.roles.other || "unspecified"} onChange={value => setRole("other", value)} onExpand={() => onBranchAction("expand", "other")} onCollapse={() => onBranchAction("collapse", "other")} />)}
      {kinds.flatMap(kind => ([
        card(`top-${kind}`, <ThreePositionSwitch label={`Top ${plural(title(kind))}`} value={rules.roles[`top-${kind}`] || "unspecified"} onChange={value => setRole(`top-${kind}`, value)} onExpand={() => onBranchAction("expand", `top-${kind}`)} onCollapse={() => onBranchAction("collapse", `top-${kind}`)} />),
        card(`child-${kind}`, <ThreePositionSwitch label={`${plural(title(kind))} Children`} value={rules.roles[`child-${kind}`] || "unspecified"} onChange={value => setRole(`child-${kind}`, value)} onExpand={() => onBranchAction("expand", `child-${kind}`)} onCollapse={() => onBranchAction("collapse", `child-${kind}`)} />),
        card(`childless-${kind}`, <ThreePositionSwitch label={`Childless ${plural(title(kind))}`} value={rules.roles[`childless-${kind}`] || "unspecified"} onChange={value => setRole(`childless-${kind}`, value)} onExpand={() => onBranchAction("expand", `childless-${kind}`)} onCollapse={() => onBranchAction("collapse", `childless-${kind}`)} />),
      ]))}
    </div>}
    {!collapsed && <div className="tree-view-controls-resizer" role="separator" aria-orientation="horizontal" aria-label="Resize tree filters and tree" onPointerDown={beginResize}><span /></div>}
  </section>;
}
