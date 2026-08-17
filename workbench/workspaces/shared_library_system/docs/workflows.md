[← Back to top-level README](../../../../README.md)

# Workflows

A Workflow is a filesystem-backed graph of Operation steps. The designer shows
that graph as a reusable execution cascade: each step binds named inputs from
workflow inputs or upstream outputs, selects an abstract Operation, and publishes
named outputs for later steps.

## Reading the designer

- The Resource Browser on the left is the Workflow tree.
- Each node opens the same reusable Operation Playground used elsewhere.
- Running a step populates compatible downstream inputs with its real outputs.
- Completed playground details collapse so the next unrun step stays visible.
- **Run cascade** executes the dependency graph using the implementation choices
  currently selected in the step playgrounds.
- Optional probes can inspect intermediate artifacts without blocking the direct
  path unless a specialization explicitly makes them required.

## Populate Inputs

The compact **Populate Inputs** band is a testing aid available on executable
resource playgrounds:

When an Operation declares no inputs, the band reports **No inputs to populate**
instead of offering population actions that cannot apply.

- **Last Output** loads the newest compatible output from the workspace.
- **Random Output** chooses a compatible output at random.
- **Sample's Input** restores the resource's saved example input.
- **Empty/Null** clears text and image values and nulls structured values.

These actions prepare one step for inspection; they do not rewrite the saved
Workflow binding.

Operations with no inputs, such as a server-discovery step, show **No inputs to
populate** in the band instead of presenting irrelevant actions.

## Operations and durable executions

An Operation is a reusable capability, while an Execution is a durable runtime
attempt to invoke it. In the designer, execution state appears where it is
actionable: step status, results, errors, evidence, events, and logs. A Codex
task or thread is separate from both the Operation contract and its Execution.

## Dataflow bindings

Bindings beginning with `$` resolve from Workflow context. For example, a
chooser may publish `(element game)` and the next Operation may bind
`(game $game)`. After the chooser runs, the designer populates the next
playground's `game` input with the selected object, making the cascade visible
and individually testable before the whole Workflow runs.
