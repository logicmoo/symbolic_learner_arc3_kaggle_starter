# Learn a Visual World by Observation

[← Back to repository README](../../../../README.md)

## Purpose

Learn how a visual world changes by binding the world, preserving a before state, observing a real action, preserving an after state, explaining the transition, and asking a human whether another observation cycle is needed.

## Inputs and outputs

The workflow receives a `world`, an initial `observation`, and a `result_observation`. It returns a `transition` record and a Boolean `decision` indicating whether to continue observing.

## Workflow

1. Select and retain the supplied world.
2. Capture the initial observation in the context of that selected world.
3. Convert the initial observation into an object-oriented before-state representation.
4. Pause for a human to describe or select the action that was actually observed.
5. After the action is known, capture the supplied result observation as the after-state representation.
6. Compare the before and after representations and produce a transition record. This comparison depends on both states.
7. Present the transition to a human and ask whether to repeat the observation process or conclude.

## Control and acceptance requirements

The continuation decision is an explicit human output, not an inferred loop condition. If the workflow is embedded in a larger repetition loop, that loop must be bounded and use this decision as its condition. Preserve the selected world, both observations, the observed action, the transition explanation, and the decision as linked evidence.
