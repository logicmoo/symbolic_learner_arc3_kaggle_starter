# Message to MicroAtoms

[← Back to repository README](../../../../README.md)

## Purpose

Turn an OmegaClaw exchange into small, provenance-bearing memory atoms, review their annotations, persist the memory record, and test whether the stored memory helps a weaker model produce better-grounded behavior.

## Inputs and outputs

The workflow receives a `message`, its `conversation_context`, a weaker-model control value without memory, and a weaker-model value with memory. It returns the persisted `microatoms` record and comparative `groundingEvidence`.

## Workflow

1. Capture the exchange without losing its original message content.
2. Decompose the captured message into the smallest meaningful staged micro-atoms.
3. Pause for a human to review and amend the atom annotations.
4. Persist the staged atoms with the conversation context as a provenance-bearing memory record. This step depends on both staging and human review.
5. Run the weaker-model control that does not receive the stored memory.
6. Separately run the weaker-model condition that does receive the stored memory. Both conditions begin from the same persisted record and remain independently identifiable.
7. Compare the two weaker-model results.
8. Combine that comparison with the persisted micro-atom record and publish memory-grounding evidence.

## Acceptance requirements

Keep the with-memory and without-memory conditions separate until the comparison step. A reported advantage must be traceable to the persisted record and both control results. Preserve the human annotations and conversation context in provenance; do not treat an unreviewed staging value as the final memory record.
