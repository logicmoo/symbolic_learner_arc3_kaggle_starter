[← Back to top-level README](../../../../README.md)

# AtomSpaces and Runtime Contexts

An AtomSpace design resource declares the named AtomSpaces, environment references, parameters, and knowledge bindings available to a Goal Run or Workflow Run. AtomSpace specifications describe the required binding contract; implementations provide concrete bindings for a workspace.

Design resources live under `design/atomspaces/`. Shared AtomSpaces are inherited, while a workspace resource with the same `id` overrides the shared definition. A same-kind `implements` relationship defines a concrete implementation; property reuse is independently declared by `inheritsFrom`.

At runtime, the selected AtomSpace bindings are resolved into a durable run context. That runtime Context is a snapshot of the binding set used by the run; it does not silently reread mutable design resources. Older workspaces may still be read from legacy `contexts/` paths, but new resources are saved under `design/atomspaces/`.

The **Resource AtomSpace** subpage materializes all effective design, policy,
knowledge, and runtime resources as atoms. It exposes implementation,
property-inheritance, availability, and preferred-implementation links and can
emit the filtered graph as MeTTa.
