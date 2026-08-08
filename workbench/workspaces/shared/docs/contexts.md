[← Back to top-level README](../../../../README.md)

# AtomSpaces and Runtime Contexts

An AtomSpace design resource declares the named AtomSpaces, environment references, parameters, and knowledge bindings available to a Goal Run or Workflow Run. AtomSpace specifications describe the required binding contract; variants provide concrete bindings for a workspace.

These design resources remain filesystem resources under `contexts/` for schema compatibility. Shared AtomSpaces are inherited, while a workspace file with the same `id` overrides the shared resource. At runtime, the resolved variant becomes a Context attached to a durable run. Runtime Context records preserve that resolved binding set rather than silently reading mutable ambient configuration.
