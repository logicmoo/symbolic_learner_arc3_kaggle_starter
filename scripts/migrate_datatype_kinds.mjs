import fs from "node:fs";
import path from "node:path";

const shared = path.resolve("workbench", "workspaces", "shared");
const semanticDirectory = path.join(shared, "datatypes");
const representationDirectory = path.join(shared, "representations");
const concreteDirectory = path.join(shared, "concrete_datatypes");
const configDirectory = path.join(shared, "config");
const concreteId = id => id === "plain_text" ? "text_plain" : id;
const ids = value => [...new Set((Array.isArray(value) ? value : []).map(String).filter(Boolean))];
const title = value => value.split("_").map(word => word ? word[0].toUpperCase() + word.slice(1) : word).join(" ");

fs.mkdirSync(concreteDirectory, { recursive: true });

for (const name of fs.readdirSync(semanticDirectory).filter(name => name.endsWith(".json"))) {
  const source = path.join(semanticDirectory, name);
  const document = JSON.parse(fs.readFileSync(source, "utf8"));
  if (document.kind !== "datatype" && document.kind !== "semantic_datatype") continue;
    document.kind = "semantic_datatype";
    if (document.extends) {
      document.parents = ids([...(document.parents ?? []), ...ids(document.extends)]);
      delete document.extends;
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
    document.children = encodings.map(encoding => concreteId(String(encoding.id))).filter(Boolean);
    if (document.children.length) document.preferredChild ??= document.children[0];
    delete document.encodings;
  }

  for (const encoding of encodings ?? []) {
    if (!encoding?.id) continue;
    const id = concreteId(String(encoding.id));
    const current = concrete.get(id) ?? { kind: "concrete_datatype", id, label: title(id), parents: [], mimeTypes: [], extensions: [] };
    current.parents = ids([...current.parents, document.id]);
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
