import fs from "node:fs";
import path from "node:path";

const workspaceRoot = path.resolve("workbench", "workspaces");
const families = {
  goal_variant: { parentKind: "goal" },
  plan_variant: { parentKind: "plan" },
  operation_implementation: { parentKind: "operation" },
  prompt_implementation: { parentKind: "prompt" },
  datatype_representation: { parentKind: "datatype" },
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
  record.workspace = path.relative(workspaceRoot, record.file).split(path.sep)[0];
  byWorkspaceAndId.set(`${record.workspace}:${record.document.id}`, record);
}

for (const child of records) {
  const family = families[child.document.kind];
  if (!family) continue;
  child.document.parents = ids(child.document.parents);

  for (const parentId of child.document.parents) {
    const parent = byWorkspaceAndId.get(`${child.workspace}:${parentId}`) ?? byWorkspaceAndId.get(`shared:${parentId}`);
    if (!parent || parent.document.kind !== family.parentKind) {
      throw new Error(`${child.document.kind}:${child.document.id} points to missing ${family.parentKind}:${parentId}`);
    }
    parent.document.children = ids(parent.document.children);
    if (!parent.document.children.includes(child.document.id)) parent.document.children.push(child.document.id);
  }
}

let changed = 0;
for (const record of records) {
  if (record.original === JSON.stringify(record.document)) continue;
  fs.writeFileSync(record.file, `${JSON.stringify(record.document, null, 2)}\n`, "utf8");
  changed += 1;
}
console.log(`Synchronized flat parent/child relationships in ${changed} resource files.`);
