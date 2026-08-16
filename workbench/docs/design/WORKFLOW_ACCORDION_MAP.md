[Back to repository README](../../../README.md)

# Workflow Accordion Map

Use the exact visible accordion name when assigning new workflow-page content.
New controls must be placed full-width inside the named existing accordion.
Do not create a new accordion, card, toolbar, floating panel, side control, or
custom layout unless the user explicitly requests a new accordion.

## CENTER STACK

Stack ID: `center-stack`

`CENTER STACK` is structurally the entire workspace column between the
Menu/Resource boundary and the Docs boundary. Its direct accordion members
naturally occupy that column. Do not add CSS resizing or per-member width and
positioning workarounds.

1. `ENGLISH SPECIFICATION EDITOR`
2. `MEMORY / VALUE PLAN`
3. `GENERATE DRAFT`
4. `VALIDATION RESULTS`
5. `APPLY TO WORKFLOW`
6. `PREFLIGHT SPLINE`
7. `LEFT + RIGHT`
8. `RUNNER DESIGN REFERENCE`

The `GENERATE DRAFT` accordion contains the complete rich Operation runner.
Inferred values are ordinary content inside `MEMORY / VALUE PLAN`; they do not
create another accordion stack.

`LEFT + RIGHT` contains the complete `LEFT STACK` and `RIGHT STACK`; it does
not merely control two stacks rendered elsewhere.

## LEFT STACK

Stack ID: `left-stack`

- `WORKFLOW RUNNER`
- `STAGE <number> OF <total>`
- Workflow step playground members

`WORKFLOW RUNNER` is the first direct member, above the selected Stage.

## RIGHT STACK

Stack ID: `right-stack`

- `WORKFLOW RUNS`
- `SELECTED RUN SPLINE`
- Runtime values and detected-object members

## Placement contract

When the user says “put this in `<accordion name>`,” add it to that existing
member's body. Preserve the member's full-width behavior and its native
collapse, scroll, full, and drag behavior through `ThreeStateAccordionStack`
and `ThreeStateAccordionMember`.

No fourth workflow-page accordion stack is permitted unless the user explicitly
changes this three-stack architecture.
