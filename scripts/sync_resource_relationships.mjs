import fs from "node:fs";
import path from "node:path";

const workspaceRoot = path.resolve("workbench", "workspaces");
const families = {
  goal_variant: { parentKind: "goal" },
  plan_variant: { parentKind: "plan" },
  operation_implementation: { parentKind: "operation" },
  prompt_implementation: { parentKind: "prompt" },
  representation_datatype: { parentKind: "semantic_datatype" },
  concrete_datatype: { parentKind: "representation_datatype" },
  model_policy_variant: { parentKind: "model_policy" },
};

function filesBelow(directory, result = []) {
  if (!fs.existsSync(directory)) return result;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) filesBelow(target, result);
    else if (entry.name.endsWith(".json")) result.push(target);
  }
  return result;
}

function ids(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [];
  return Object.keys(value).filter(value => value.trim());
}
const inheritanceGrant = () => ({ lend: ["*"], withhold: ["id", "label", "description", "enabled", "implements", "implementedBy", "preferredImplementation", "inheritsFrom", "inheritedBy", "dependsOn", "dependedOnBy"] });
const implementationMap = values => Object.fromEntries(ids(values).map(id => [id, {}]));

const records = [];
for (const file of filesBelow(workspaceRoot)) {
  try {
    const document = JSON.parse(fs.readFileSync(file, "utf8"));
    if (document?.specializations && !document.implementedBy) {
      document.implementedBy = implementationMap(document.specializations);
      document.inheritedBy = document.specializations;
      delete document.specializations;
    }
    if (document?.preferredSpecialization && !document.preferredImplementation) {
      document.preferredImplementation = document.preferredSpecialization;
      delete document.preferredSpecialization;
    }
    if (document?.implements && !document.inheritsFrom && Object.values(document.implements).some(policy => policy?.borrow || policy?.exclude)) {
      document.inheritsFrom = document.implements;
    }
    if (document?.implements) document.implements = implementationMap(document.implements);
    if (document?.kind && document?.id) records.push({ file, document, original: JSON.stringify(document) });
  } catch {
    // Non-resource and temporarily invalid JSON files are outside this migration.
  }
}

const byWorkspaceAndId = new Map();
for (const record of records) {
  record.workspace = path.relative(workspaceRoot, record.file).split(path.sep)[0];
  byWorkspaceAndId.set(`${record.workspace}:${record.document.id}`, record);
}

for (const parent of records) {
  if (!parent.document.implementedBy || Array.isArray(parent.document.implementedBy)) continue;
  parent.document.implementedBy = Object.fromEntries(ids(parent.document.implementedBy).filter(implementationId => {
    const implementation = byWorkspaceAndId.get(`${parent.workspace}:${implementationId}`) ?? byWorkspaceAndId.get(`shared:${implementationId}`);
    return implementation && ids(implementation.document.implements).includes(parent.document.id);
  }).map(implementationId => [implementationId, {}]));
}

for (const child of records) {
  const family = families[child.document.kind];
  if (!family && !child.document.implements) continue;
  const implementedIds = ids(child.document.implements);

  for (const parentId of implementedIds) {
    const parent = byWorkspaceAndId.get(`${child.workspace}:${parentId}`) ?? byWorkspaceAndId.get(`shared:${parentId}`);
    const allowedParentKinds = family
      ? [family.parentKind, ...(child.document.kind === "semantic_datatype" ? ["semantic_datatype"] : [])]
      : [child.document.kind];
    if (!parent || !allowedParentKinds.includes(parent.document.kind)) {
      throw new Error(`${child.document.kind}:${child.document.id} points to invalid parent:${parentId}`);
    }
    parent.document.implementedBy = parent.document.implementedBy && !Array.isArray(parent.document.implementedBy) ? parent.document.implementedBy : {};
    parent.document.implementedBy[child.document.id] ??= {};
  }
  for (const parentId of ids(child.document.inheritsFrom)) {
    const parent = byWorkspaceAndId.get(`${child.workspace}:${parentId}`) ?? byWorkspaceAndId.get(`shared:${parentId}`);
    if (!parent) throw new Error(`${child.document.id} inherits from missing resource:${parentId}`);
    parent.document.inheritedBy ??= {};
    parent.document.inheritedBy[child.document.id] ??= inheritanceGrant();
  }
  for (const dependencyId of ids(child.document.dependsOn)) {
    const dependency = byWorkspaceAndId.get(`${child.workspace}:${dependencyId}`) ?? byWorkspaceAndId.get(`shared:${dependencyId}`);
    if (!dependency) throw new Error(`${child.document.id} depends on missing resource:${dependencyId}`);
    dependency.document.dependedOnBy ??= {};
    dependency.document.dependedOnBy[child.document.id] ??= {};
  }
}

let changed = 0;
for (const record of records) {
  if (record.original === JSON.stringify(record.document)) continue;
  fs.writeFileSync(record.file, `${JSON.stringify(record.document, null, 2)}\n`, "utf8");
  changed += 1;
}
console.log(`Synchronized implementation, inheritance, and dependency relationships in ${changed} resource files.`);
