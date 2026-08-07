# Universal Artifact Editor

The workbench is an Artifact Editor rather than a collection of unrelated IDEs.

Every first-class resource has two identities:

- semantic identity: what the artifact means or promises;
- implementation identity: how a concrete variant realizes that contract.

Examples include abstract operations with Python, Prolog, MeTTa, and LLM implementations; abstract datatypes with Bitmap, Scene Graph, LOGO/Turtle, Object Facts, Natural Language, and embedding representations; and abstract prompts with model-, language-, or optimization-specific prompt implementations.

## UI baseline: Operations b42249b

The user-designated `b42249b` Operations editor is the feature baseline for the universal editor. The global editor may gain features from Data, Prompts, Models, workflow tooling, or later panels, but it must not become a lowest-common-denominator editor that removes the rich Operations behavior.

The showcase contract is `echo_into_titlecased` with Python, Prolog, and LLM implementations. That example makes variant selection and implementation-specific editing visible immediately.

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

The canonical React chrome lives in `UniversalArtifactEditor.tsx`. `HierarchyResourceEditor.tsx` is retained only as a compatibility alias so existing artifact-family adapters automatically use the same global editor. Artifact-family adapters provide hierarchy data and the rich type-specific editor body; they must not reimplement or remove the shared navigation, tabs, split comparison, generic inspection, or dock behavior.

## Resource families

The architecture is intended to cover Operations, Datatypes, Prompts, Converters, Validators, Scorers, Knowledge Bases, Workflows, Datasets, Resources, Models, and future artifact kinds.

### Operation variants

Operation implementations retain rich implementation-specific views. Python implementations expose module/file/class/callable information. Prolog implementations expose predicates and arity. MeTTa implementations expose MeTTa configuration. LLM implementations expose model/profile dispatch and ordered prompt bindings.

The Operations page is also the regression oracle for the shared chrome: if the universal editor cannot still present the full rich Operations experience, the abstraction has removed too much.

### Datatype variants

Datatype representations expose encoding/schema/parser/serializer/MIME information and may provide live viewers such as Bitmap preview, Scene Graph viewer, Turtle/LOGO viewer, or natural-language preview. The abstract datatype chooses a preferred representation without changing workflows.

### Prompt variants

Prompt implementations expose editable prompt text, targets, versions, variables, expected inputs/outputs, model targeting, evaluation history, and comparison with other prompt variants. The abstract prompt chooses a preferred prompt alternative.

### Model variants

Model/back-end/profile resources use the same editor shell while retaining inheritance/configuration controls and resolved runtime configuration.

## No-feature-loss rule

The effective global editor feature set is the union of useful capabilities found in the rich Operations baseline and later artifact panels. New adapters add specialized behavior; they do not replace the baseline with a simpler generic form.

A source-level regression test in `tests/test_universal_artifact_editor_ui.py` protects the major baseline features and verifies that Operations, Data, Prompts, and Models still route through the universal editor.

## Workflow independence

A workflow references semantic specifications. It should not have to be rewritten to switch between Python and Prolog, one prompt version and another, or Bitmap and Scene Graph. Variant selection and representation conversion are planner/runtime concerns and remain inspectable in the editor.
