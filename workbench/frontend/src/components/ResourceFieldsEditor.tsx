import {
  DEFAULT_IMPLEMENTATION_INHERITANCE,
  DEFAULT_SPECIALIZATION_INHERITANCE,
  implementationInheritanceMap,
  relationshipIds,
  specializationInheritanceMap,
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
  onCreateSpecialization,
  relatedResources,
}: {
  resource: ResourceDocument;
  sourceScope: string;
  onChange: (source: string) => void;
  resourceHref: (id: string) => string;
  onCreateSpecialization?: () => void;
  relatedResources?: ResourceDocument[];
}) {
  const update = (key: string, value: unknown, remove = false) => {
    const next = { ...resource };
    if (remove) delete next[key];
    else next[key] = value;
    onChange(JSON.stringify(next, null, 2));
  };
  const implementedIds = resourceImplementedIds(resource);
  const implementationPolicies = implementationInheritanceMap(resource.implements);
  const specializationPolicies = specializationInheritanceMap(resource.specializations);
  const selectorList = (raw: string) => [...new Set(raw.split(/[\n,]+/).map(value => value.trim()).filter(Boolean))];
  const updateImplementedIds = (raw: string) => {
    const ids = selectorList(raw);
    update("implements", Object.fromEntries(ids.map(id => [id, implementationPolicies[id] || {
      borrow: [...DEFAULT_IMPLEMENTATION_INHERITANCE.borrow],
      exclude: [...DEFAULT_IMPLEMENTATION_INHERITANCE.exclude],
    }])));
  };
  const updateImplementationPolicy = (id: string, key: "borrow" | "exclude", raw: string) =>
    update("implements", {
      ...implementationPolicies,
      [id]: { ...implementationPolicies[id], [key]: selectorList(raw) },
    });
  const updateSpecializationPolicy = (id: string, key: "lend" | "withhold", raw: string) =>
    update("specializations", {
      ...specializationPolicies,
      [id]: { ...specializationPolicies[id], [key]: selectorList(raw) },
    });
  const kind = String(resource.kind || resource.type || resource.subkind || "resource");
  const specializations = relationshipIds(resource.specializations);
  const abstractness = deriveResourceAbstractness(resource, relatedResources);

  return <section className="resource-fields-section">
    <div className="llm-subhead">
      <div>
        <span>RESOURCE FIELDS</span>
        <b>Structured identity, lifecycle, and inheritance properties</b>
      </div>
      {onCreateSpecialization && <button type="button" onClick={onCreateSpecialization}>+ Specialization</button>}
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
        <span>IMPLEMENTS</span>
        <input
          value={implementedIds.join(", ")}
          placeholder="No implemented resource — family root"
          onChange={event => updateImplementedIds(event.target.value)}
        />
        {implementedIds.length > 0 && <nav aria-label="Implemented resources">
          {implementedIds.map(id => <a key={id} href={resourceHref(id)}>Edit implemented resource · {id}</a>)}
        </nav>}
        {implementedIds.length > 0 && <div className="resource-inheritance-policies">
          {implementedIds.map(id => {
            const policy = implementationPolicies[id] || DEFAULT_IMPLEMENTATION_INHERITANCE;
            return <article key={id}>
              <b>{id}</b>
              <label><span>BORROW</span><input value={policy.borrow.join(", ")} onChange={event => updateImplementationPolicy(id, "borrow", event.target.value)} /></label>
              <label><span>EXCLUDE</span><input value={policy.exclude.join(", ")} placeholder="none" onChange={event => updateImplementationPolicy(id, "exclude", event.target.value)} /></label>
            </article>;
          })}
        </div>}
      </div>
      <div className="wide resource-field-specializations">
        <span>SPECIALIZATIONS</span>
        {specializations.length > 0
          ? <>
              <nav aria-label="Resource specializations">{specializations.map(id => <a key={id} href={resourceHref(id)}>Open specialization · {id}</a>)}</nav>
              <div className="resource-inheritance-policies">
                {specializations.map(id => {
                  const policy = specializationPolicies[id] || DEFAULT_SPECIALIZATION_INHERITANCE;
                  return <article key={id}>
                    <b>{id}</b>
                    <label><span>LEND</span><input value={policy.lend.join(", ")} onChange={event => updateSpecializationPolicy(id, "lend", event.target.value)} /></label>
                    <label><span>WITHHOLD</span><input value={policy.withhold.join(", ")} onChange={event => updateSpecializationPolicy(id, "withhold", event.target.value)} /></label>
                  </article>;
                })}
              </div>
            </>
          : <b>No declared specializations</b>}
      </div>
      <div className="wide">
        <span>PREFERRED ALTERNATIVE</span>
        <select
          value={String(resource.preferredSpecialization || "")}
          disabled={specializations.length === 0}
          onChange={event => update("preferredSpecialization", event.target.value, !event.target.value)}
        >
          <option value="">planner-selected</option>
          {specializations.map(id => <option key={id} value={id}>{id}</option>)}
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
