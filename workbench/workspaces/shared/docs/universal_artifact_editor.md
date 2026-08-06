# Universal Artifact Editor

The workbench is an Artifact Editor rather than a collection of unrelated IDEs.

Every first-class resource has two identities:

- semantic identity: what the artifact means or promises;
- implementation identity: how a concrete variant realizes that contract.

Examples include abstract tasks with Python, Prolog, MeTTa, and LLM implementations; abstract datatypes with Bitmap, Scene Graph, LOGO/Turtle, Object Facts, Natural Language, and embedding representations; and abstract prompts with model-, language-, or optimization-specific prompt implementations.

## Shared editor contract

All artifact families use the same interaction model:

1. A repository/specification hierarchy on the left.
2. The semantic specification as the parent node.
3. Concrete variants beneath it.
4. A preferred/default variant selector on the specification.
5. Persistent multi-document editor tabs.
6. Side-by-side comparison/split editing.
7. Common artifact metadata and state inspection.
8. Type-specific rich editor panels in the center.
9. Documentation and contextual help in the far-right workbench inspector.
10. Optional bottom docks for documentation, history, tests, benchmarks, diff, and logs.

The shared React chrome lives in `HierarchyResourceEditor.tsx`. Artifact-family adapters provide the hierarchy data and the type-specific editor body; they should not reimplement tabbing, split view, navigation, or generic artifact inspection.

## Resource families

The architecture is intended to cover Tasks, Datatypes, Prompts, Converters, Validators, Scorers, Knowledge Bases, Workflows, Datasets, Resources, Models, and future artifact kinds.

### Task variants

Task implementations retain rich implementation-specific views. Python implementations expose module/file/class/callable information. Prolog implementations expose predicates and arity. MeTTa implementations expose MeTTa configuration. LLM implementations expose model/profile dispatch and ordered prompt bindings.

### Datatype variants

Datatype representations expose encoding/schema/parser/serializer/MIME information and may later provide live viewers such as Bitmap preview, Scene Graph viewer, Turtle/LOGO viewer, or natural-language preview.

### Prompt variants

Prompt implementations expose editable prompt text, targets, versions, variables, expected inputs/outputs, model targeting, evaluation history, and comparison with other prompt variants.

### Model variants

Model/back-end/profile resources use the same editor shell while retaining inheritance/configuration controls and resolved runtime configuration.

## Workflow independence

A workflow references semantic specifications. It should not have to be rewritten to switch between Python and Prolog, one prompt version and another, or Bitmap and Scene Graph. Variant selection and representation conversion are planner/runtime concerns and remain inspectable in the editor.
