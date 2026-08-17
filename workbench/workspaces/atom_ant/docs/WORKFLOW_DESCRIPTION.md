# Atom.Ant Symbolic Reasoning Loop

[← Back to repository README](../../../../README.md)

## Purpose

Turn a request into executable symbolic content. Produce an initial Atomese candidate, measure whether it covers the request, try a bounded collection of repairs when needed, select an adequate candidate, and return the candidate together with its final assessment.

## Inputs and outputs

The workflow receives the original `request` and an ordered array of `repair_candidates`. It returns one `report` containing the selected Atomese and the final symbolic-coverage assessment.

## Workflow

1. Reason about the request and retain the resulting reasoning trace as an explicit workflow value.
2. Generate initial Atomese from that reasoning trace.
3. Assess the initial candidate. Record the candidate, whether it is adequate, and a coverage score.
4. Fan out across at most five supplied repair candidates. Apply the semantic repair operation to each candidate and collect the repaired results in their stable input order.
5. Select the first non-empty repaired candidate as the adequate Atomese candidate.
6. Assess the selected candidate again and record its final adequacy and coverage.
7. Merge the selected Atomese with its final assessment and publish the execution report.

## Control and acceptance requirements

The repair stage is a bounded `for each` operation with a maximum of five items. The generated workflow must preserve the distinction between the initial assessment and the final assessment, must not invent repair candidates, and must not execute an unassessed candidate. If no adequate repair is available, the report must make that failure explicit rather than silently claiming coverage.
