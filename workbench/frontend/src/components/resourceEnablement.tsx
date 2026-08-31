export type EnablementResource = { enabled?: unknown } | null | undefined;

export type ResourceEnablement = {
  enabled: boolean;
  source: "self" | "dependency" | "default";
};

export function resolveResourceEnablement(resource: EnablementResource, dependencies: ResourceEnablement[] = []): ResourceEnablement {
  if (resource?.enabled === false) return { enabled: false, source: "self" };
  if (dependencies.some(dependency => !dependency.enabled)) return { enabled: false, source: "dependency" };
  if (resource?.enabled === true) return { enabled: true, source: "self" };
  return { enabled: true, source: "default" };
}

export function enablementClass(state: ResourceEnablement): string {
  return state.enabled ? "resource-enabled" : "resource-disabled";
}

export function ResourceEnablementBadge({ state }: { state: ResourceEnablement }) {
  const label = state.source === "dependency" ? "dependency off" : state.enabled ? "enabled" : "disabled";
  return <span className={`resource-enablement-badge ${enablementClass(state)}`} title={`Effective availability: ${label}`}>{label}</span>;
}
