import {
  DEFAULT_INHERITANCE_GRANT,
  DEFAULT_INHERITANCE_REQUEST,
  inheritanceGrantMap,
  inheritanceRequestMap,
  relationshipIds,
} from "./resourceRelationships";
import { deriveResourceAbstractness } from "./resourceAbstractness";

type ResourceDocument = Record<string, unknown>;

export function resourceImplementedIds(resource: ResourceDocument): string[] {
  return relationshipIds(resource.implements);
}

export function ResourceFieldsEditor({
  resource,
  sourceScope,
  onChange,
  resourceHref,
  onCreateImplementation,
  relatedResources,
}: {
  resource: ResourceDocument;
  sourceScope: string;
  onChange: (source: string) => void;
  resourceHref: (id: string) => string;
  onCreateImplementation?: () => void;
  relatedResources?: ResourceDocument[];
}) {
  const update = (key: string, value: unknown, remove = false) => {
    const next = { ...resource };
    if (remove) delete next[key];
    else next[key] = value;
    onChange(JSON.stringify(next, null, 2));
  };
  const implementedIds = resourceImplementedIds(resource);
  const implementedByIds = relationshipIds(resource.implementedBy);
  const inheritedFromIds = relationshipIds(resource.inheritsFrom);
  const inheritedByIds = relationshipIds(resource.inheritedBy);
  const inheritanceRequestPolicies = inheritanceRequestMap(resource.inheritsFrom);
  const inheritanceGrantPolicies = inheritanceGrantMap(resource.inheritedBy);
  const selectorList = (raw: string) => [...new Set(raw.split(/[\n,]+/).map(value => value.trim()).filter(Boolean))];
  const updateImplementedIds = (raw: string) => {
    const ids = selectorList(raw);
    update("implements", Object.fromEntries(ids.map(id => [id, {}])));
  };
  const updateInheritedFromIds = (raw: string) => {
    const ids = selectorList(raw);
    update("inheritsFrom", Object.fromEntries(ids.map(id => [id, inheritanceRequestPolicies[id] || {
      borrow: [...DEFAULT_INHERITANCE_REQUEST.borrow],
      exclude: [...DEFAULT_INHERITANCE_REQUEST.exclude],
    }])));
  };
  const updateInheritanceRequestPolicy = (id: string, key: "borrow" | "exclude", raw: string) =>
    update("inheritsFrom", {
      ...inheritanceRequestPolicies,
      [id]: { ...inheritanceRequestPolicies[id], [key]: selectorList(raw) },
    });
  const updateInheritanceGrantPolicy = (id: string, key: "lend" | "withhold", raw: string) =>
    update("inheritedBy", {
      ...inheritanceGrantPolicies,
      [id]: { ...inheritanceGrantPolicies[id], [key]: selectorList(raw) },
    });
  const kind = String(resource.kind || resource.type || resource.subkind || "resource");
  const dependencyIds = relationshipIds(resource.dependsOn);
  const dependentIds = relationshipIds(resource.dependedOnBy);
  const abstractness = deriveResourceAbstractness(resource, relatedResources);

  return <section className="resource-fields-section">
    <div className="llm-subhead">
      <div>
        <span>RESOURCE FIELDS</span>
        <b>Structured identity, lifecycle, and inheritance properties</b>
      </div>
      {onCreateImplementation && <button type="button" onClick={onCreateImplementation}>+ Implementation</button>}
    </div>
    <div className="operation-abstract-summary resource-fields-editor">
      <div className="resource-field-enabled">
        <span>ENABLED</span>
        <label>
          <input
            type="checkbox"
            checked={resource.enabled !== false}
            onChange={event => update("enabled", event.target.checked)}
          />
          <b>{resource.enabled !== false ? "Enabled" : "Disabled"}</b>
        </label>
      </div>
      <div>
        <span>KIND</span>
        <input value={kind} readOnly />
      </div>
      <div>
        <span>ID</span>
        <input value={String(resource.id || "")} onChange={event => update("id", event.target.value)} />
      </div>
      <div>
        <span>SOURCE</span>
        <input value={sourceScope} readOnly />
      </div>
      <div className={`wide resource-derived-status resource-derived-status--${abstractness.status}`}>
        <span>DERIVED IMPLEMENTATION</span>
        <div className="resource-derived-status-heading">
          <b>{abstractness.status.toUpperCase()}</b>
          <small>{abstractness.summary}</small>
        </div>
        <div className="resource-derived-status-metrics">
          <code>{abstractness.localFieldCount} local</code>
          <code>{abstractness.borrowed.length} borrowed</code>
          <code>{abstractness.withheld.length} withheld</code>
          <code>{abstractness.conflicts.length} conflicts</code>
        </div>
        {abstractness.obligations.length > 0 && <div className="resource-derived-obligations">
          <strong>UNRESOLVED</strong>
          {abstractness.obligations.map(item => <code key={item}>{item}</code>)}
        </div>}
        {(abstractness.borrowed.length > 0 || abstractness.excluded.length > 0 || abstractness.withheld.length > 0) && <details>
          <summary>Inheritance provenance</summary>
          {abstractness.borrowed.length > 0 && <p><b>BORROWED</b> {abstractness.borrowed.join(" · ")}</p>}
          {abstractness.excluded.length > 0 && <p><b>EXCLUDED</b> {abstractness.excluded.join(" · ")}</p>}
          {abstractness.withheld.length > 0 && <p><b>WITHHELD</b> {abstractness.withheld.join(" · ")}</p>}
        </details>}
      </div>
      <div className="wide">
        <span>LABEL</span>
        <input value={String(resource.label || "")} onChange={event => update("label", event.target.value)} />
      </div>
      <div className="wide resource-field-implements">
        <span>IMPLEMENTS · IMPLEMENTATION / CLASSIFICATION</span>
        <input
          value={implementedIds.join(", ")}
          placeholder="No implemented interface or abstract resource"
          onChange={event => updateImplementedIds(event.target.value)}
        />
        {implementedIds.length > 0 && <nav aria-label="Implemented resources">
          {implementedIds.map(id => <a key={id} href={resourceHref(id)}>Edit implemented resource · {id}</a>)}
        </nav>}
      </div>
      <div className="wide resource-field-inherits-from">
        <span>INHERITS FROM · PROPERTY INHERITANCE</span>
        <input
          value={inheritedFromIds.join(", ")}
          placeholder="No property-inheritance parents"
          onChange={event => updateInheritedFromIds(event.target.value)}
        />
        {inheritedFromIds.length > 0 && <nav aria-label="Inherited resources">
          {inheritedFromIds.map(id => <a key={id} href={resourceHref(id)}>Edit inherited resource · {id}</a>)}
        </nav>}
        {inheritedFromIds.length > 0 && <div className="resource-inheritance-policies">
          {inheritedFromIds.map(id => {
            const policy = inheritanceRequestPolicies[id] || DEFAULT_INHERITANCE_REQUEST;
            return <article key={id}>
              <b>{id}</b>
              <label><span>BORROW</span><input value={policy.borrow.join(", ")} onChange={event => updateInheritanceRequestPolicy(id, "borrow", event.target.value)} /></label>
              <label><span>EXCLUDE</span><input value={policy.exclude.join(", ")} placeholder="none" onChange={event => updateInheritanceRequestPolicy(id, "exclude", event.target.value)} /></label>
            </article>;
          })}
        </div>}
      </div>
      <div className="wide resource-field-implemented-by">
        <span>IMPLEMENTED BY · REVERSE IMPLEMENTATION LINKS</span>
        {implementedByIds.length > 0
          ? <nav aria-label="Resource implementations">{implementedByIds.map(id => <a key={id} href={resourceHref(id)}>Open implementation · {id}</a>)}</nav>
          : <b>No declared implementations</b>}
      </div>
      <div className="wide resource-field-inherited-by">
        <span>INHERITED BY · REVERSE PROPERTY LINKS</span>
        {inheritedByIds.length > 0
          ? <>
              <nav aria-label="Inheriting resources">{inheritedByIds.map(id => <a key={id} href={resourceHref(id)}>Open inheriting resource · {id}</a>)}</nav>
              <div className="resource-inheritance-policies">
                {inheritedByIds.map(id => {
                  const policy = inheritanceGrantPolicies[id] || DEFAULT_INHERITANCE_GRANT;
                  return <article key={id}>
                    <b>{id}</b>
                    <label><span>LEND</span><input value={policy.lend.join(", ")} onChange={event => updateInheritanceGrantPolicy(id, "lend", event.target.value)} /></label>
                    <label><span>WITHHOLD</span><input value={policy.withhold.join(", ")} onChange={event => updateInheritanceGrantPolicy(id, "withhold", event.target.value)} /></label>
                  </article>;
                })}
              </div>
            </>
          : <b>No declared inheriting resources</b>}
      </div>
      <div className="wide resource-field-dependencies">
        <span>DEPENDS ON · AVAILABILITY PREREQUISITES</span>
        <input
          value={dependencyIds.join(", ")}
          placeholder="No availability dependencies"
          onChange={event => update("dependsOn", Object.fromEntries(selectorList(event.target.value).map(id => [id, {}])))}
        />
        {dependencyIds.length > 0 && <nav aria-label="Resource dependencies">
          {dependencyIds.map(id => <a key={id} href={resourceHref(id)}>Open dependency · {id}</a>)}
        </nav>}
      </div>
      <div className="wide resource-field-dependents">
        <span>DEPENDED ON BY · SYNCHRONIZED REVERSE LINKS</span>
        {dependentIds.length > 0
          ? <nav aria-label="Dependent resources">{dependentIds.map(id => <a key={id} href={resourceHref(id)}>Open dependent · {id}</a>)}</nav>
          : <b>No declared dependents</b>}
      </div>
      <div className="wide">
        <span>PREFERRED IMPLEMENTATION</span>
        <select
          value={String(resource.preferredImplementation || "")}
          disabled={implementedByIds.length === 0}
          onChange={event => update("preferredImplementation", event.target.value, !event.target.value)}
        >
          <option value="">planner-selected</option>
          {implementedByIds.map(id => <option key={id} value={id}>{id}</option>)}
        </select>
      </div>
      <div className="wide">
        <span>DESCRIPTION</span>
        <textarea
          value={String(resource.description || "")}
          onChange={event => update("description", event.target.value)}
        />
      </div>
    </div>
  </section>;
}
