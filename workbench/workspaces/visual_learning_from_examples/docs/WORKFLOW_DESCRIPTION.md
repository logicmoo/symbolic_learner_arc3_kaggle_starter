# Examples to Visual Memory

[← Back to repository README](../../../../README.md)

## Purpose

Turn a supplied set of visual examples into a stable, human-reviewed learning batch and publish it as a durable memory-silo record.

## Inputs and outputs

The workflow receives an array named `examples` and returns one durable `memory` value named `memory_silo`.

## Workflow

1. Capture the supplied examples as a stable evidence collection.
2. Normalize that collection into a learning batch whose ordering and representation can be reproduced.
3. Pause for a human to review whether the normalized examples are recognizable and suitable for learning.
4. Publish the memory silo only after both the normalized batch and the review record exist.
5. Merge the normalized examples with the human review and return the resulting memory record.

## Acceptance requirements

Do not publish directly from the raw examples or omit the human review. Retain provenance from the input collection through normalization and review to the published memory. The normalization step must not silently add examples or discard rejected examples without recording that decision.
