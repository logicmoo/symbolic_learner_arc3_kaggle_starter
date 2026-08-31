import fs from "node:fs";
import path from "node:path";

const shared = path.resolve("workbench", "workspaces", "shared");
const semanticDirectory = path.join(shared, "datatypes");
const representationDirectory = path.join(shared, "representations");
const concreteDirectory = path.join(shared, "concrete_datatypes");
const configDirectory = path.join(shared, "config");
const concreteId = id => id === "plain_text" ? "text_plain" : id;
const ids = value => [...new Set((Array.isArray(value) ? value : []).map(String).filter(Boolean))];
const implementationMap = values => Object.fromEntries(ids(values).map(id => [id, {}]));
const inheritanceMap = values => Object.fromEntries(ids(values).map(id => [id, { borrow: ["*"], exclude: [] }]));
const implementedByMap = values => Object.fromEntries(ids(values).map(id => [id, {}]));
const title = value => value.split("_").map(word => word ? word[0].toUpperCase() + word.slice(1) : word).join(" ");
const semanticParentOverrides = {
  human_intervention: ["intervention"],
  objectified_observation: ["observation"],
};

fs.mkdirSync(concreteDirectory, { recursive: true });

for (const name of fs.readdirSync(semanticDirectory).filter(name => name.endsWith(".json"))) {
  const source = path.join(semanticDirectory, name);
  const document = JSON.parse(fs.readFileSync(source, "utf8"));
  if (document.kind !== "datatype" && document.kind !== "semantic_datatype") continue;
    document.kind = "semantic_datatype";
    if (document.extends) {
      const parents = [...Object.keys(document.implements ?? {}), ...ids(document.extends)];
      document.implements = implementationMap(parents);
      document.inheritsFrom = inheritanceMap(parents);
      delete document.extends;
    }
    if (document.id !== "information") {
      const parents = semanticParentOverrides[document.id] ?? ["information"];
      document.implements = implementationMap(parents);
      document.inheritsFrom = inheritanceMap(parents);
    }
  const target = path.join(semanticDirectory, `${document.id}.semantic_datatype.json`);
  fs.writeFileSync(target, `${JSON.stringify(document, null, 2)}\n`);
  if (target !== source) fs.unlinkSync(source);
}

const concrete = new Map();
for (const name of fs.readdirSync(representationDirectory).filter(name => name.endsWith(".json"))) {
  const source = path.join(representationDirectory, name);
  const document = JSON.parse(fs.readFileSync(source, "utf8"));
  if (document.kind !== "datatype_representation" && document.kind !== "representation_datatype") continue;
  document.kind = "representation_datatype";
  const encodings = Array.isArray(document.encodings) ? document.encodings : null;
  if (encodings) {
    const specializationIds = encodings.map(encoding => concreteId(String(encoding.id))).filter(Boolean);
    document.implementedBy = implementedByMap(specializationIds);
    if (specializationIds.length) document.preferredImplementation ??= specializationIds[0];
    delete document.encodings;
  }

  for (const encoding of encodings ?? []) {
    if (!encoding?.id) continue;
    const id = concreteId(String(encoding.id));
    const current = concrete.get(id) ?? { kind: "concrete_datatype", id, label: title(id), implements: {}, mimeTypes: [], extensions: [] };
    const parents = [...Object.keys(current.implements), document.id];
    current.implements = implementationMap(parents);
    current.inheritsFrom = inheritanceMap(parents);
    current.mimeTypes = ids([...current.mimeTypes, ...(encoding.mimeTypes ?? [])]);
    current.extensions = ids([...current.extensions, ...(encoding.extensions ?? [])]);
    concrete.set(id, current);
  }

  const target = path.join(representationDirectory, `${document.id}.representation_datatype.json`);
  fs.writeFileSync(target, `${JSON.stringify(document, null, 2)}\n`);
  if (target !== source) fs.unlinkSync(source);
}

for (const document of concrete.values()) {
  fs.writeFileSync(path.join(concreteDirectory, `${document.id}.concrete_datatype.json`), `${JSON.stringify(document, null, 2)}\n`);
}

for (const name of fs.readdirSync(configDirectory).filter(name => name.endsWith(".datatype_catalog.json"))) {
  const source = path.join(configDirectory, name);
  const document = JSON.parse(fs.readFileSync(source, "utf8"));
  document.kind = "config";
  document.legacy = true;
  const target = path.join(configDirectory, name.replace(".datatype_catalog.json", ".legacy.config.json"));
  fs.writeFileSync(target, `${JSON.stringify(document, null, 2)}\n`);
  if (target !== source) fs.unlinkSync(source);
}

console.log(`Migrated semantic, representation, and ${concrete.size} concrete datatype resources.`);
