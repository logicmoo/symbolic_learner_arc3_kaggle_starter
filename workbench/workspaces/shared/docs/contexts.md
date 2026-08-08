[← Back to top-level README](../../../../README.md)

# Contexts

A Context declares the named AtomSpaces, environment references, parameters, and knowledge bindings available to a Goal Run or Workflow Run. Context specifications describe the required binding contract; Context variants provide concrete bindings for a workspace or runtime.

Contexts are filesystem resources under `contexts/`. Shared contexts are inherited, while a workspace file with the same `id` overrides the shared resource. Runtime records preserve the resolved Context variant rather than silently reading mutable ambient configuration.
