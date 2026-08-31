export type InheritanceRequestPolicy = {
  borrow: string[];
  exclude: string[];
};

export type InheritanceGrantPolicy = {
  lend: string[];
  withhold: string[];
};

export const DEFAULT_INHERITANCE_REQUEST: InheritanceRequestPolicy = {
  borrow: ["*"],
  exclude: [],
};

export const DEFAULT_INHERITANCE_GRANT: InheritanceGrantPolicy = {
  lend: ["*"],
  withhold: ["id", "label", "description", "enabled", "implements", "implementedBy", "preferredImplementation", "inheritsFrom", "inheritedBy", "dependsOn", "dependedOnBy"],
};

export function implementsResource(id: string): Record<string, Record<string, never>> {
  return { [id]: {} };
}

export function implementedByResource(id: string): Record<string, Record<string, never>> {
  return { [id]: {} };
}

export function inheritsFromResource(id: string): Record<string, InheritanceRequestPolicy> {
  return {
    [id]: {
      borrow: [...DEFAULT_INHERITANCE_REQUEST.borrow],
      exclude: [...DEFAULT_INHERITANCE_REQUEST.exclude],
    },
  };
}

export function inheritedByResource(id: string): Record<string, InheritanceGrantPolicy> {
  return {
    [id]: {
      lend: [...DEFAULT_INHERITANCE_GRANT.lend],
      withhold: [...DEFAULT_INHERITANCE_GRANT.withhold],
    },
  };
}

export function dependsOnResource(id: string): Record<string, Record<string, never>> {
  return { [id]: {} };
}

export function dependedOnByResource(id: string): Record<string, Record<string, never>> {
  return { [id]: {} };
}

function selectors(value: unknown, fallback: string[]): string[] {
  if (!Array.isArray(value)) return [...fallback];
  return [...new Set(value.map(String).map(item => item.trim()).filter(Boolean).map(item => {
    if (item === "specializations" || item.startsWith("specializations.")) return item.replace("specializations", "implementedBy");
    if (item === "preferredSpecialization" || item.startsWith("preferredSpecialization.")) return item.replace("preferredSpecialization", "preferredImplementation");
    return item;
  }))];
}

export function relationshipIds(value: unknown): string[] {
  const values = value && typeof value === "object" && !Array.isArray(value)
    ? Object.keys(value)
    : Array.isArray(value)
      ? value
      : typeof value === "string"
        ? [value]
        : [];
  return [...new Set(values.map(String).map(item => item.trim()).filter(Boolean))];
}

export function inheritanceRequestMap(value: unknown): Record<string, InheritanceRequestPolicy> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return Object.fromEntries(Object.entries(value).map(([id, raw]) => {
    const policy = raw && typeof raw === "object" && !Array.isArray(raw) ? raw as Record<string, unknown> : {};
    return [id, {
      borrow: selectors(policy.borrow, DEFAULT_INHERITANCE_REQUEST.borrow),
      exclude: selectors(policy.exclude, DEFAULT_INHERITANCE_REQUEST.exclude),
    }];
  }));
}

export function inheritanceGrantMap(value: unknown): Record<string, InheritanceGrantPolicy> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return Object.fromEntries(Object.entries(value).map(([id, raw]) => {
    const policy = raw && typeof raw === "object" && !Array.isArray(raw) ? raw as Record<string, unknown> : {};
    return [id, {
      lend: selectors(policy.lend, DEFAULT_INHERITANCE_GRANT.lend),
      withhold: selectors(policy.withhold, DEFAULT_INHERITANCE_GRANT.withhold),
    }];
  }));
}

export function normalizeResourceRelationships(resource: Record<string, unknown>): Record<string, unknown> {
  const normalized = { ...resource };
  const legacyImplementedBy = resource.specializations;
  const rawImplements = resource.implements;
  if (normalized.implementedBy === undefined && legacyImplementedBy !== undefined) {
    normalized.implementedBy = Object.fromEntries(relationshipIds(legacyImplementedBy).map(id => [id, {}]));
  }
  if (normalized.inheritedBy === undefined && legacyImplementedBy !== undefined) {
    normalized.inheritedBy = inheritanceGrantMap(legacyImplementedBy);
  }
  if (normalized.preferredImplementation === undefined && resource.preferredSpecialization !== undefined) {
    normalized.preferredImplementation = resource.preferredSpecialization;
  }
  if (normalized.inheritsFrom === undefined && rawImplements && typeof rawImplements === "object" && !Array.isArray(rawImplements)) {
    const policies = rawImplements as Record<string, unknown>;
    if (Object.values(policies).some(value => value !== null && typeof value === "object" && ("borrow" in value || "exclude" in value))) {
      normalized.inheritsFrom = inheritanceRequestMap(rawImplements);
    }
  }
  if (rawImplements !== undefined) {
    normalized.implements = Object.fromEntries(relationshipIds(rawImplements).map(id => [id, {}]));
  }
  delete normalized.specializations;
  delete normalized.preferredSpecialization;
  const preferred = String(normalized.preferredImplementation || "");
  if (preferred && !relationshipIds(normalized.implementedBy).includes(preferred)) {
    throw new Error(`preferredImplementation ${preferred} must belong to implementedBy`);
  }
  return normalized;
}
