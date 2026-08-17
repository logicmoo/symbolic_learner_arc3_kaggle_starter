# Learn and Test an ARC3 Transformation Rule

[← Back to repository README](../../../../README.md)

## Purpose

Learn a transformation rule from a real ARC3 before/action/after example, retain competing explanations instead of hiding uncertainty, use the reviewed rule to predict an unseen case, and grade the prediction only after an independent outcome is available.

## Inputs and outputs

The workflow receives a `before` image, an `after` image, the intervening `action`, supporting `evidence`, an `unseen_case`, and its later `observed_outcome`. It returns the induced candidate `rules`, the prediction for the unseen case, and an independent `grade` of that prediction.

## Workflow

1. Capture the before image as preserved evidence.
2. Independently capture the after image as preserved evidence.
3. Compare those captures and identify observed changes and object correspondences.
4. Use the transition and supplied evidence to induce multiple rival candidate rules. Do not prematurely collapse them into one explanation.
5. Pause for a human to review the rules, their assumptions, critiques, and evidence, and select a reviewed rule.
6. Apply the reviewed rule and supplied action to the unseen case. Record this prediction before observing its outcome.
7. Compare the recorded prediction with the later independent outcome and produce the prediction grade.

## Acceptance requirements

Preserve the dependency chain and the separation between training evidence, the held-out prediction, and grading evidence. The prediction must not depend on `observed_outcome`; only the final grading step may consume it. Retain enough provenance to trace every rule, prediction, review decision, and grade to the values that produced it.
