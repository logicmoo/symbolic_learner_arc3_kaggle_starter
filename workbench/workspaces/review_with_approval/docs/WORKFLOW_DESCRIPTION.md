# Review with Approval

[← Back to repository README](../../../../README.md)

## Purpose

Demonstrate a durable human checkpoint: preserve an arbitrary payload, pause for explicit human approval, and return the approval decision without pretending that the machine approved its own work.

## Inputs and outputs

The workflow receives a `payload` of any supported type. It returns a Boolean `result` containing the human's approval decision.

## Workflow

1. Copy the supplied payload into a stable intermediate value named `copied`.
2. Pause at a human step that depends on the completed copy.
3. Present the approval form and require the human to provide the Boolean `approved` value.
4. Return that value as the workflow result.

## Acceptance requirements

The approval step must not run before the payload has been copied. The decision must come from the human form, not from a default or inferred machine value. Preserve the copied payload and approval event in the run record so a later reviewer can see what was approved and by whom.
