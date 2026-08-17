[← Back to top-level README](../../../../README.md)

# Workspace Data

Knowledge **Data** contains the values that humans, imported datasets, and
Workflows operate on: images, text, demonstrations, tables, and other binary or
structured inputs. Datatype specifications are defined separately under
**Capabilities → Datatypes**.

Use **Import Data** to add one or more files. A collection name stores them at:

```text
knowledge/data/<collection>/
```

For example, importing `before.png` and `after.png` into collection `scene-12`
creates `knowledge/data/scene-12/before.png` and
`knowledge/data/scene-12/after.png`. Existing files are protected unless
**Replace same-name files** is selected.

Selecting an image shows a preview and metadata. **Open original** serves the
persisted workspace asset directly. Legacy value folders such as `data/`,
`datasets/`, `images/`, `inputs/`, and `examples/` remain visible.

Data and Artifacts are related but distinct:

```text
Data                         Artifact
input or reusable value  →  produced/imported typed result
knowledge/data/...           knowledge/artifacts/... or runtime/.../artifacts/...
```

Repository documentation:

- [Browse Data documents](?docs=data)
- [Browse datatype documents](?docs=datatype)
- [Open Symbolic Datatypes in AtomSpace Explained](../../../../docs/DATATYPES_MANIFEST_EXPLAINED.md)
