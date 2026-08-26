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
const specializationPolicy = () => ({ lend: ["*"], withhold: ["id", "label", "description", "implements", "specializations", "preferredSpecialization"] });

const records = [];
for (const file of filesBelow(workspaceRoot)) {
  try {
    const document = JSON.parse(fs.readFileSync(file, "utf8"));
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
  if (!parent.document.specializations || Array.isArray(parent.document.specializations)) continue;
  parent.document.specializations = Object.fromEntries(ids(parent.document.specializations).filter(specializationId => {
    const specialization = byWorkspaceAndId.get(`${parent.workspace}:${specializationId}`) ?? byWorkspaceAndId.get(`shared:${specializationId}`);
    return specialization && ids(specialization.document.implements).includes(parent.document.id);
  }).map(specializationId => [specializationId, parent.document.specializations[specializationId]]));
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
    parent.document.specializations = parent.document.specializations && !Array.isArray(parent.document.specializations) ? parent.document.specializations : {};
    parent.document.specializations[child.document.id] ??= specializationPolicy();
  }
}

let changed = 0;
for (const record of records) {
  if (record.original === JSON.stringify(record.document)) continue;
  fs.writeFileSync(record.file, `${JSON.stringify(record.document, null, 2)}\n`, "utf8");
  changed += 1;
}
console.log(`Synchronized flat implements/specializations relationships in ${changed} resource files.`);
