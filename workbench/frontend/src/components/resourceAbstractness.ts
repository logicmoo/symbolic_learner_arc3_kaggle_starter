import {
  DEFAULT_INHERITANCE_GRANT,
  DEFAULT_INHERITANCE_REQUEST,
  inheritanceGrantMap,
  inheritanceRequestMap,
  relationshipIds,
} from "./resourceRelationships";

type ResourceDocument = Record<string, unknown>;
type FlatDocument = Record<string, unknown>;

export type ResourceImplementationStatus = "abstract" | "partial" | "concrete" | "runnable";

export type ResourceAbstractness = {
  status: ResourceImplementationStatus;
  summary: string;
  obligations: string[];
  borrowed: string[];
  excluded: string[];
  withheld: string[];
  conflicts: string[];
  missingResources: string[];
  localFieldCount: number;
  delegatedTo?: string;
};

const RELATIONSHIP_FIELDS = new Set(["id", "enabled", "implements", "implementedBy", "preferredImplementation", "inheritsFrom", "inheritedBy", "dependsOn", "dependedOnBy"]);

function isObject(value: unknown): value is ResourceDocument {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function flatten(value: unknown, prefix = "", result: FlatDocument = {}): FlatDocument {
  if (!isObject(value)) {
    if (prefix) result[prefix] = value;
    return result;
  }
  for (const [key, child] of Object.entries(value)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (isObject(child) && Object.keys(child).length > 0) flatten(child, path, result);
    else result[path] = child;
  }
  return result;
}

function unflatten(value: FlatDocument): ResourceDocument {
  const result: ResourceDocument = {};
  for (const [path, child] of Object.entries(value)) {
    const parts = path.split(".");
    let target = result;
    for (const part of parts.slice(0, -1)) {
      if (!isObject(target[part])) target[part] = {};
      target = target[part] as ResourceDocument;
    }
    target[parts.at(-1)!] = child;
  }
  return result;
}

function selectorMatches(path: string, selector: string): boolean {
  if (selector === "*") return true;
  if (selector.endsWith(".*")) {
    const prefix = selector.slice(0, -2);
    return path === prefix || path.startsWith(`${prefix}.`);
  }
  return path === selector || path.startsWith(`${selector}.`);
}

function selected(path: string, selectors: string[]): boolean {
  return selectors.some(selector => selectorMatches(path, selector));
}

function sameValue(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}

function hasContent(value: unknown): boolean {
  if (typeof value === "string") return Boolean(value.trim());
  if (Array.isArray(value)) return value.length > 0;
  if (isObject(value)) return Object.keys(value).length > 0;
  return value !== undefined && value !== null;
}

type FieldResolution = {
  effective: ResourceDocument;
  local: FlatDocument;
  borrowed: string[];
  excluded: string[];
  withheld: string[];
  conflicts: string[];
  missingResources: string[];
};

function resolveFields(
  resource: ResourceDocument,
  byId: Map<string, ResourceDocument>,
  trail: string[] = [],
): FieldResolution {
  const resourceId = String(resource.id || "");
  const local = flatten(resource);
  if (resourceId && trail.includes(resourceId)) {
    return {
      effective: resource,
      local,
      borrowed: [],
      excluded: [],
      withheld: [],
      conflicts: [`cycle: ${[...trail, resourceId].join(" -> ")}`],
      missingResources: [],
    };
  }
  const inherited: FlatDocument = {};
  const inheritedSources = new Map<string, string>();
  const borrowed: string[] = [];
  const excluded: string[] = [];
  const withheld: string[] = [];
  const conflicts: string[] = [];
  const missingResources: string[] = [];
  const inheritancePolicies = inheritanceRequestMap(resource.inheritsFrom);

  for (const inheritedId of relationshipIds(resource.inheritsFrom)) {
    const inheritedResource = byId.get(inheritedId);
    if (!inheritedResource) {
      missingResources.push(inheritedId);
      continue;
    }
    const parentResolution = resolveFields(inheritedResource, byId, [...trail, resourceId].filter(Boolean));
    conflicts.push(...parentResolution.conflicts);
    missingResources.push(...parentResolution.missingResources);
    const request = inheritancePolicies[inheritedId] || DEFAULT_INHERITANCE_REQUEST;
    const grants = inheritanceGrantMap(inheritedResource.inheritedBy);
    if (!grants[resourceId]) conflicts.push(`missing backlink: ${inheritedId}.inheritedBy[${resourceId}]`);
    const grant = grants[resourceId] || DEFAULT_INHERITANCE_GRANT;
    for (const [path, value] of Object.entries(flatten(parentResolution.effective))) {
      if (RELATIONSHIP_FIELDS.has(path.split(".")[0])) continue;
      if (!selected(path, request.borrow) || !selected(path, grant.lend)) continue;
      if (selected(path, request.exclude)) {
        excluded.push(`${inheritedId}:${path}`);
        continue;
      }
      if (selected(path, grant.withhold)) {
        withheld.push(`${inheritedId}:${path}`);
        continue;
      }
      if (path in local) continue;
      if (path in inherited && !sameValue(inherited[path], value)) {
        conflicts.push(`${path}: ${inheritedSources.get(path)} <> ${inheritedId}`);
        delete inherited[path];
        inheritedSources.delete(path);
        continue;
      }
      inherited[path] = value;
      inheritedSources.set(path, inheritedId);
      borrowed.push(`${inheritedId}:${path}`);
    }
  }
  return {
    effective: unflatten({ ...inherited, ...local }),
    local,
    borrowed: [...new Set(borrowed)].sort(),
    excluded: [...new Set(excluded)].sort(),
    withheld: [...new Set(withheld)].sort(),
    conflicts: [...new Set(conflicts)].sort(),
    missingResources: [...new Set(missingResources)].sort(),
  };
}

function effectiveMarkers(kind: string, effective: ResourceDocument): { runnable: boolean; concrete: boolean; obligations: string[] } {
  if (kind === "operation") {
    return {
      runnable: hasContent(effective.implementation),
      concrete: hasContent(effective.implementation),
      obligations: hasContent(effective.implementation) ? [] : ["execution route"],
    };
  }
  if (kind === "prompt") {
    const complete = hasContent(effective.text);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["prompt body"] };
  }
  if (kind === "prompt_profile") {
    const complete = hasContent(effective.prompts);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["ordered prompts"] };
  }
  if (kind === "workflow") {
    const complete = hasContent(effective.steps);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["workflow steps"] };
  }
  if (kind === "planning_strategy") {
    const complete = hasContent(effective.workflow) || hasContent(effective.planner) || hasContent(effective.implementation);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["workflow or planner binding"] };
  }
  if (kind === "model") {
    const complete = hasContent(effective.model) || hasContent((effective.configuration as ResourceDocument | undefined)?.defaultModel);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["provider model binding"] };
  }
  if (kind === "backend" || kind === "system") {
    const complete = hasContent(effective.provider);
    return { runnable: complete, concrete: complete, obligations: complete ? [] : ["provider binding"] };
  }
  if (kind === "concrete_datatype") {
    const complete = hasContent(effective.encoding) || hasContent(effective.mimeTypes) || hasContent(effective.extensions);
    return { runnable: false, concrete: complete, obligations: complete ? [] : ["encoding, MIME type, or extension"] };
  }
  if (kind === "goal") {
    const complete = hasContent(effective.successCriteria);
    return { runnable: false, concrete: complete, obligations: complete ? [] : ["success criteria"] };
  }
  if (kind === "atomspace") {
    const complete = hasContent(effective.bindings) || hasContent(effective.schema) || hasContent(effective.atoms);
    return { runnable: false, concrete: complete, obligations: complete ? [] : ["bindings, schema, or atoms"] };
  }
  if (kind.includes("policy")) {
    const complete = hasContent(effective.rules) || hasContent(effective.query) || hasContent(effective.models);
    return { runnable: false, concrete: complete, obligations: complete ? [] : ["policy rules or query"] };
  }
  return { runnable: false, concrete: false, obligations: [] };
}

export function deriveResourceAbstractness(
  resource: ResourceDocument,
  relatedResources: ResourceDocument[] = [],
  trail: string[] = [],
): ResourceAbstractness {
  const resourceId = String(resource.id || "");
  if (resourceId && trail.includes(resourceId)) {
    return {
      status: "abstract",
      summary: "Inheritance cycle prevents resolution.",
      obligations: ["acyclic inheritance path"],
      borrowed: [],
      excluded: [],
      withheld: [],
      conflicts: [`cycle: ${[...trail, resourceId].join(" -> ")}`],
      missingResources: [],
      localFieldCount: 0,
    };
  }

  const byId = new Map(relatedResources.flatMap(item => item.id ? [[String(item.id), item] as const] : []));
  if (resourceId) byId.set(resourceId, resource);
  const resolution = resolveFields(resource, byId);
  const { effective, local, borrowed, excluded, withheld, conflicts, missingResources } = resolution;

  const kind = String(resource.kind || resource.type || "resource");
  const marker = effectiveMarkers(kind, effective);
  const obligations = [...marker.obligations];
  if (missingResources.length) obligations.push(...missingResources.map(id => `available parent ${id}`));
  if (conflicts.length) obligations.push(...conflicts.map(item => `resolve ${item}`));

  const preferredId = String(resource.preferredImplementation || "");
  let delegated: ResourceAbstractness | null = null;
  if (!marker.runnable && preferredId) {
    const preferred = byId.get(preferredId);
    if (preferred) delegated = deriveResourceAbstractness(preferred, relatedResources, [...trail, resourceId].filter(Boolean));
    else {
      missingResources.push(preferredId);
      obligations.push(`available preferred implementation ${preferredId}`);
    }
  }

  const runnableThroughPreferred = delegated?.status === "runnable";
  const concreteThroughPreferred = delegated?.status === "concrete";
  const unresolved = obligations.length > 0 && !runnableThroughPreferred && !concreteThroughPreferred;
  const meaningfulLocalFields = Object.keys(local).filter(path => !RELATIONSHIP_FIELDS.has(path.split(".")[0]) && !["kind", "label", "description", "enabled"].includes(path.split(".")[0]));
  const hasProgress = meaningfulLocalFields.length > 0 || borrowed.length > 0 || relationshipIds(resource.implements).length > 0;
  const status: ResourceImplementationStatus = runnableThroughPreferred || marker.runnable
    ? "runnable"
    : concreteThroughPreferred || (marker.concrete && !unresolved)
      ? "concrete"
      : hasProgress
        ? "partial"
        : "abstract";
  const delegatedTo = runnableThroughPreferred || concreteThroughPreferred ? preferredId : undefined;
  const unresolvedObligations = delegatedTo ? [] : obligations;
  const summary = delegatedTo
    ? `${status === "runnable" ? "Runnable" : "Concrete"} through preferred implementation ${delegatedTo}.`
    : status === "runnable"
      ? "Required execution behavior resolves."
      : status === "concrete"
        ? "The resource's non-executable job is fully specified."
        : status === "partial"
          ? `${unresolvedObligations.length} unresolved obligation${unresolvedObligations.length === 1 ? "" : "s"} remain.`
          : "The job remains substantially unimplemented.";

  return {
    status,
    summary,
    obligations: unresolvedObligations,
    borrowed: [...new Set(borrowed)].sort(),
    excluded: [...new Set(excluded)].sort(),
    withheld: [...new Set(withheld)].sort(),
    conflicts: [...new Set(conflicts)].sort(),
    missingResources: [...new Set(missingResources)].sort(),
    localFieldCount: meaningfulLocalFields.length,
    delegatedTo,
  };
}
