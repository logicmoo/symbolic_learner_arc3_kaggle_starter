# Game Preview Gallery: intentionally costly example

[Back to repository README](../../../README.md)

The ARC3 Random Player exposes one optional `Curate Viewable Gallery` step that opens every available game, captures its first frame, and returns a single Gallery Resource. This is intentionally a nontrivially bad demonstration, not recommended architecture.

Opening the complete remote catalog is slow, consumes server resources, creates many action-tree files, and fetches images that random selection will immediately discard. It exists to make the cost visible and to prove that an inspection-gallery resource can be inserted anywhere in a workflow.

Better placements usually include:

- after filtering or ranking a catalog;
- around a small candidate set;
- after a meaningful state transition;
- at a human or AI review boundary;
- on cached artifacts instead of live environments.

The ARC3-specific curation Operation performs preview capture and gallery construction as one workflow step. Humans and the Workbench UI can render its entries, while AI and downstream Operations consume the same artifact without a parallel UI-only representation.
