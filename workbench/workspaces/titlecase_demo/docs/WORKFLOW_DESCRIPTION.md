# Titlecase Demo

[← Back to repository README](../../../../README.md)

## Purpose

Demonstrate the smallest useful semantic workflow: accept text, invoke an abstract titlecasing operation, and return the transformed text while allowing runtime preflight to choose the concrete implementation.

## Inputs and outputs

The workflow receives one `text` value and returns one `text` value named `titlecased_text`.

## Workflow

1. Bind the workflow input to the `text` port of the semantic operation `echo_into_titlecased`.
2. Resolve that abstract operation to an available concrete implementation during preflight or runtime.
3. Execute the operation exactly once.
4. Bind its `titlecased_text` output to the workflow output.

## Acceptance requirements

Preserve the abstract operation boundary; the workflow must not hard-code a particular Python, Prolog, or LLM implementation. The returned text should retain the original words and spacing wherever the selected implementation permits while applying title casing. Record the resolved implementation in the run for reproducibility.
