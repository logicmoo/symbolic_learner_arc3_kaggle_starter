# Count to Ten — Workflow Generation Test

## Purpose

This project is a deliberately small acceptance test for generating a semantic workflow from an English resource. Its complete domain is counting integers from one through ten.

## Required behavior

The generated workflow must count from **1 through 10 inclusive**. It must preserve the ordered result `[1,2,3,4,5,6,7,8,9,10]`, finish with `final_count = 10`, and retain iteration evidence.

The workflow initializes `current_count` to `1` and `collected_values` to an empty ordered list. Each iteration reads `current_count`, appends it to `collected_values`, and records provenance. While the current value is less than `10`, it increments the value and returns to the capture step.

The loop is explicitly bounded to at most ten iterations. It may not append `11`, skip a value, reorder values, or overwrite the accumulated list.

## Memory model

- `current_count` is a retained workflow-scoped `atomspace_cell`.
- `collected_values` is an accumulated workflow-scoped `atomspace_cell`.
- Every write declares `atomspace_scope`, `atomspace_scope_key`, `atomspace_cell`, `atomspace_atom`, `change_mode`, and `evidenceLink`.
- Incrementing the counter uses `change_mode = increment`.
- Capturing a number uses `change_mode = append`.

## Generation contract

Use the inherited operation `workflow.populate_from_english` with prompt resource `generate_count_to_ten.english_workflow_specification`. The effective shared operation catalog and workflow schema are authoritative.

Generate semantic operations first. Preflight validates bindings, infers retained and accumulated loop values, and resolves control arcs. Concrete Python, Prolog, or LLM implementations are selected or produced only after the complete semantic workflow exists.

## Acceptance checks

1. The generated workflow has no unresolved `$value` bindings.
2. Every dependency and loop target references an existing step.
3. The loop has an explicit finite bound.
4. `collected_values` is accumulated rather than replaced.
5. Runtime output is exactly `[1,2,3,4,5,6,7,8,9,10]`.
6. `final_count` is exactly `10`.
7. Every captured value has iteration provenance.
