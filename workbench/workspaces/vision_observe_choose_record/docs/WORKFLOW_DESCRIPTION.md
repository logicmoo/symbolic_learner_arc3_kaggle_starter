# Observe, Choose, and Record

[← Back to repository README](../../../../README.md)

## Purpose

Carry a visual observation through a human action choice and create one durable record that keeps the chosen action connected to the observation that motivated it.

## Inputs and outputs

The workflow receives one `observation` object and returns one combined `record` named `action_record`.

## Workflow

1. Capture the supplied observation as `captured_observation` without changing its meaning.
2. After the capture exists, pause for a human to choose an action.
3. Merge the captured observation and the chosen action into one action record. This step depends on both values and must not run while either is missing.
4. Return the combined action record.

## Acceptance requirements

Do not choose the action automatically or separate it from its source observation. The returned record must contain enough structure and provenance to recover both the observation and the human decision. Preserve the human-input event in runtime evidence.
