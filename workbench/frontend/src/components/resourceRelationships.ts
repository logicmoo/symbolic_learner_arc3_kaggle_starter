export type ImplementationInheritancePolicy = {
  borrow: string[];
  exclude: string[];
};

export type SpecializationInheritancePolicy = {
  lend: string[];
  withhold: string[];
};

export const DEFAULT_IMPLEMENTATION_INHERITANCE: ImplementationInheritancePolicy = {
  borrow: ["*"],
  exclude: [],
};

export const DEFAULT_SPECIALIZATION_INHERITANCE: SpecializationInheritancePolicy = {
  lend: ["*"],
  withhold: ["id", "label", "description", "implements", "specializations", "preferredSpecialization"],
};

export function implementsResource(id: string): Record<string, ImplementationInheritancePolicy> {
  return {
    [id]: {
      borrow: [...DEFAULT_IMPLEMENTATION_INHERITANCE.borrow],
      exclude: [...DEFAULT_IMPLEMENTATION_INHERITANCE.exclude],
    },
  };
}

export function specializesResource(id: string): Record<string, SpecializationInheritancePolicy> {
  return {
    [id]: {
      lend: [...DEFAULT_SPECIALIZATION_INHERITANCE.lend],
      withhold: [...DEFAULT_SPECIALIZATION_INHERITANCE.withhold],
    },
  };
}

function selectors(value: unknown, fallback: string[]): string[] {
  if (!Array.isArray(value)) return [...fallback];
  return [...new Set(value.map(String).map(item => item.trim()).filter(Boolean))];
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

export function implementationInheritanceMap(value: unknown): Record<string, ImplementationInheritancePolicy> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return Object.fromEntries(Object.entries(value).map(([id, raw]) => {
    const policy = raw && typeof raw === "object" && !Array.isArray(raw) ? raw as Record<string, unknown> : {};
    return [id, {
      borrow: selectors(policy.borrow, DEFAULT_IMPLEMENTATION_INHERITANCE.borrow),
      exclude: selectors(policy.exclude, DEFAULT_IMPLEMENTATION_INHERITANCE.exclude),
    }];
  }));
}

export function specializationInheritanceMap(value: unknown): Record<string, SpecializationInheritancePolicy> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return Object.fromEntries(Object.entries(value).map(([id, raw]) => {
    const policy = raw && typeof raw === "object" && !Array.isArray(raw) ? raw as Record<string, unknown> : {};
    return [id, {
      lend: selectors(policy.lend, DEFAULT_SPECIALIZATION_INHERITANCE.lend),
      withhold: selectors(policy.withhold, DEFAULT_SPECIALIZATION_INHERITANCE.withhold),
    }];
  }));
}
