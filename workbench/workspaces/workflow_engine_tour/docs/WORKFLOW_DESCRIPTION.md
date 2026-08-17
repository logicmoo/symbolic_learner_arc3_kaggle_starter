# Fan Out and Merge

[← Back to repository README](../../../../README.md)

## Purpose

Demonstrate bounded workflow fan-out and deterministic collection. Apply one operation independently to every supplied item, then merge the per-item values into one ordered workflow output.

## Inputs and outputs

The workflow receives an `items` array and returns an array named `values`.

## Workflow

1. Iterate over the supplied items in their original order.
2. For each item, bind that item to the `value` port of the map operation and execute it independently.
3. Allow no more than 20 items in one run.
4. Collect the values emitted by every completed map invocation.
5. After fan-out has completed, run the collection operation and return the collected values.

## Control and acceptance requirements

The map stage is an explicit bounded `for each` operation with `maxItems` equal to 20. The collect stage depends on completion of the map stage. Preserve stable item ordering and per-item provenance, and make overflow or individual-item failure explicit rather than silently dropping values.
