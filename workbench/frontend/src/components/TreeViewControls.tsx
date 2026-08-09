import type { TreeVisibilityRule, TreeVisibilityRules } from "./useArtifactTreeFilter";

function title(value: string) { return value.replace(/[_-]+/g, " ").replace(/\b\w/g, letter => letter.toUpperCase()); }
function plural(value: string) { return value.endsWith("s") ? value : `${value}s`; }

function ThreePositionSwitch({ label, value, onChange }: { label: string; value: TreeVisibilityRule; onChange: (value: TreeVisibilityRule) => void }) {
  return <div className="tree-rule-row"><span>{label}</span><div className="tree-rule-switch" role="radiogroup" aria-label={`${label} visibility`}>
    {(["show", "hide", "unspecified"] as TreeVisibilityRule[]).map(option => <button key={option} type="button" role="radio" aria-checked={value === option} className={value === option ? "active" : ""} onClick={() => onChange(option)}>{option === "unspecified" ? "—" : title(option)}</button>)}
  </div></div>;
}

export function TreeViewControls({ kinds, rules, onChange }: { kinds: string[]; rules: TreeVisibilityRules; onChange: (rules: TreeVisibilityRules) => void }) {
  const setRule = (key: "search" | "enabled" | "disabled" | "categories", value: TreeVisibilityRule) => onChange({ ...rules, [key]: value });
  const setRole = (key: string, value: TreeVisibilityRule) => onChange({ ...rules, roles: { ...rules.roles, [key]: value } });
  const kindLabels = kinds.map(title);
  const roleKeys = [...kinds.flatMap(kind => [`top-${kind}`, `child-${kind}`]), "other"];
  const allValues = [rules.search, rules.enabled, rules.disabled, rules.categories, ...roleKeys.map(key => rules.roles[key] || "unspecified")];
  const masterValue: TreeVisibilityRule = allValues.every(value => value === allValues[0]) ? allValues[0] : "unspecified";
  const setAll = (value: TreeVisibilityRule) => onChange({
    search: value,
    enabled: value,
    disabled: value,
    categories: value,
    roles: Object.fromEntries(roleKeys.map(key => [key, value])),
  });
  return <section className="tree-view-controls" aria-label="Tree View Controls">
    <header><div><b>Tree View Controls</b><span>Show, hide, or leave each dimension unspecified.</span></div><button type="button" onClick={() => onChange({ search: "unspecified", enabled: "unspecified", disabled: "unspecified", categories: "unspecified", roles: {} })}>Reset</button></header>
    <div className="tree-rule-group tree-rule-master"><b>ALL CONTROLS</b><ThreePositionSwitch label="Set Everything" value={masterValue} onChange={setAll} /></div>
    <div className="tree-rule-group"><b>SEARCH</b><ThreePositionSwitch label="Search Matches" value={rules.search} onChange={value => setRule("search", value)} /></div>
    <div className="tree-rule-group"><b>AVAILABILITY</b><ThreePositionSwitch label="Enabled" value={rules.enabled} onChange={value => setRule("enabled", value)} /><ThreePositionSwitch label="Disabled" value={rules.disabled} onChange={value => setRule("disabled", value)} /></div>
    <div className="tree-rule-group"><b>STRUCTURE</b><ThreePositionSwitch label="Categories" value={rules.categories} onChange={value => setRule("categories", value)} /></div>
    <div className="tree-rule-group"><b>RESOURCE ROLES</b>{kinds.flatMap(kind => ([
      <ThreePositionSwitch key={`top-${kind}`} label={`Top ${plural(title(kind))}`} value={rules.roles[`top-${kind}`] || "unspecified"} onChange={value => setRole(`top-${kind}`, value)} />,
      <ThreePositionSwitch key={`child-${kind}`} label={`Child ${plural(title(kind))}`} value={rules.roles[`child-${kind}`] || "unspecified"} onChange={value => setRole(`child-${kind}`, value)} />,
    ]))}<ThreePositionSwitch label={`Non-${kindLabels.join("/") || "Typed"}`} value={rules.roles.other || "unspecified"} onChange={value => setRole("other", value)} /></div>
  </section>;
}
