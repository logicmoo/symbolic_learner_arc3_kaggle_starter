# Game Preview Gallery: intentionally costly example

The ARC3 Random Player inserts the reusable `gallery.curate_resource` pattern after opening every available game and capturing its first frame. This is intentionally a nontrivially bad demonstration, not recommended architecture.

Opening the complete remote catalog is slow, consumes server resources, creates many action-tree files, and fetches images that random selection will immediately discard. It exists to make the cost visible and to prove that an inspection-gallery resource can be inserted anywhere in a workflow.

Better placements usually include:

- after filtering or ranking a catalog;
- around a small candidate set;
- after a meaningful state transition;
- at a human or AI review boundary;
- on cached artifacts instead of live environments.

The generic `gallery.curate_resource` Operation accepts any upstream collection and returns one structured `gallery_resource` artifact. Humans and the Workbench UI can render its entries, while AI and downstream Operations consume the same artifact without a parallel UI-only representation.
