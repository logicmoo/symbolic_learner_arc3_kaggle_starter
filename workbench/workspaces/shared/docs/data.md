# Data contracts

The Data page edits two first-class resource kinds:

- `datatype`: the abstract semantic meaning of information.
- `datatype_representation`: a concrete encoding or structural realization of that meaning.

The intended relationship mirrors abstract operations and operation implementations:

```text
Abstract datatype
  ├─ preferred representation
  ├─ alternative representation
  └─ alternative representation
```

For example, `image` is representation-independent while Bitmap, SVG, LOGO/Turtle, Scene Graph, Object List, Natural Language, and Embedding are interchangeable implementations of that semantic contract.

The editor deliberately uses the same rich interaction model as the Operations editor: select resources in the hierarchy on the left, keep multiple resources open as tabs, split two editors for comparison, and select the preferred representation from the abstract datatype without rewriting workflows.

Conversions are ordinary operations that connect representations. The planner may therefore choose both a operation implementation and a representation-conversion path while preserving the abstract datatype contract.
