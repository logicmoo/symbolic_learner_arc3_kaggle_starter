# Universal Artifact Editor

[Back to repository README](../../../README.md)

## Baseline

The current active application and its rich editors are the acceptance baseline. A shared editor shell must preserve the union of useful artifact-specific behavior; it must not reduce specialized editors to a generic JSON form.

## Required Capabilities

Every hierarchical artifact family should provide, where meaningful:

1. A specification parent with concrete alternatives beneath it.
2. A preferred/default alternative selector.
3. Persistent, closeable tabs with dirty markers.
4. Single-pane and split-comparison modes.
5. Rich artifact-specific controls plus interchangeable MeTTa/JSON source editing.
6. Filesystem save with shared inheritance and workspace overrides.
7. Contextual documentation on the right.
8. Tests, history, benchmarks, diffs, and logs when real data exists.
9. A playground/run surface for executable artifacts.

`UniversalArtifactEditor` supplies common hierarchy, tab, comparison, inspector, and dock chrome. `OperationLibraryEditor`, `DataCatalogPanel`, `PromptLibraryEditor`, and `LlmModelsEditor` retain ownership of their specialized panels and validation.

## Data Integrity

All nodes, alternatives, defaults, documents, and runtime results must originate in workspace files or backend APIs. Visual mockups may guide layout but cannot supply active data. Saves must retain semantic specification/implementation separation and must not collapse variants into a monolithic catalog.

## Regression Principle

Tests should assert behavior and visible capabilities of the current editor rather than bind the baseline to a historical commit identifier. UI validation must cover hierarchy selection, variant mutation, save/reload, tabs, split view, scrolling, and the executable playground.
