[← Back to top-level README](../../../../README.md)

# Data contracts

Repository documentation:

- [Browse Data documents](?docs=data)
- [Browse datatype documents](?docs=datatype)
- [Open Symbolic Datatypes in AtomSpace Explained](../../../../docs/DATATYPES_MANIFEST_EXPLAINED.md)

The Data page edits three first-class resource kinds:

- `semantic_datatype`: the abstract semantic meaning of information.
- `representation_datatype`: a general structural realization of semantic meaning.
- `concrete_datatype`: an exact encoding, MIME type, file format, or runtime form.

The intended relationship mirrors abstract operations and operation implementations:

```text
semantic_datatype
  ?? representation_datatype
       ?? concrete_datatype
```

For example, `image` is representation-independent while Bitmap, SVG, LOGO/Turtle, Scene Graph, Object List, Natural Language, and Embedding are interchangeable implementations of that semantic contract.

The editor deliberately uses the same rich interaction model as the Operations editor: select resources in the hierarchy on the left, keep multiple resources open as tabs, split two editors for comparison, and select the preferred representation from the abstract datatype without rewriting workflows.

Conversions are ordinary operations that connect representations. The planner may therefore choose both a operation implementation and a representation-conversion path while preserving the abstract datatype contract.
