import fs from "node:fs";
import path from "node:path";

const workspaceRoot = path.resolve("workbench", "workspaces");
const families = {
  goal_variant: { parentKind: "goal", childField: "implements", parentField: "variants", selection: "variantSelection" },
  plan_variant: { parentKind: "plan", childField: "implements", parentField: "variants", selection: "variantSelection" },
  operation_implementation: { parentKind: "operation", childField: "implements", parentField: "implementations", selection: "implementationSelection" },
  prompt_implementation: { parentKind: "prompt", childField: "implements", parentField: "implementations", selection: "implementationSelection" },
  datatype_representation: { parentKind: "datatype", childField: "represents", legacyChildField: "implements", parentField: "representations", selection: "representationSelection" },
  model_policy_variant: { parentKind: "model_policy", childField: "implements", parentField: "variants", selection: "variantSelection" },
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
  const values = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
  return [...new Set(values.map(String).filter(value => value.trim()))];
}

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
  const relative = path.relative(workspaceRoot, record.file);
  const workspace = relative.split(path.sep)[0];
  record.workspace = workspace;
  byWorkspaceAndId.set(`${workspace}:${record.document.id}`, record);
}

for (const child of records) {
  const family = families[child.document.kind];
  if (!family) continue;
  const parentIds = ids(child.document[family.childField] ?? child.document[family.legacyChildField]);
  child.document[family.childField] = parentIds;
  if (family.legacyChildField) delete child.document[family.legacyChildField];

  for (const parentId of parentIds) {
    const parent = byWorkspaceAndId.get(`${child.workspace}:${parentId}`)
      ?? byWorkspaceAndId.get(`shared:${parentId}`);
    if (!parent || parent.document.kind !== family.parentKind) {
      throw new Error(`${child.document.kind}:${child.document.id} points to missing ${family.parentKind}:${parentId}`);
    }
    const backlinks = ids(parent.document[family.parentField]);
    if (!backlinks.includes(child.document.id)) backlinks.push(child.document.id);
    parent.document[family.parentField] = backlinks;
    const selection = parent.document[family.selection];
    if (selection && typeof selection === "object") selection.variants = backlinks;
  }
}

let changed = 0;
for (const record of records) {
  if (record.original === JSON.stringify(record.document)) continue;
  fs.writeFileSync(record.file, `${JSON.stringify(record.document, null, 2)}\n`, "utf8");
  changed += 1;
}
console.log(`Synchronized bidirectional relationships in ${changed} resource files.`);
