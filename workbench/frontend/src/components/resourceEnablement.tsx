export type EnablementResource = { enabled?: unknown } | null | undefined;

export type ResourceEnablement = {
  enabled: boolean;
  source: "self" | "parent" | "default";
};

export function resolveResourceEnablement(resource: EnablementResource, parent?: ResourceEnablement): ResourceEnablement {
  if (resource?.enabled === true) return { enabled: true, source: "self" };
  if (resource?.enabled === false) return { enabled: false, source: "self" };
  if (parent) return { enabled: parent.enabled, source: "parent" };
  return { enabled: true, source: "default" };
}

export function enablementClass(state: ResourceEnablement): string {
  return state.enabled ? "resource-enabled" : "resource-disabled";
}

export function ResourceEnablementBadge({ state }: { state: ResourceEnablement }) {
  const label = state.source === "parent" ? `inherited ${state.enabled ? "on" : "off"}` : state.enabled ? "enabled" : "disabled";
  return <span className={`resource-enablement-badge ${enablementClass(state)}`} title={`Effective availability: ${label}`}>{label}</span>;
}
