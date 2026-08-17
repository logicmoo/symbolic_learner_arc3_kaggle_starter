# Image Perception to Recognizable Memory and ARC3

[← Back to repository README](../../../../README.md)

## Purpose

Convert an image into recognizable symbolic memory and bind that memory to an ARC3 context while retaining the evidence and provenance that led to it.

## Inputs and outputs

The workflow receives an `image` and an `arc3_context` object. It returns a context-bound `memory` value suitable for later ARC3 reasoning.

## Workflow

1. Capture the supplied image as immutable image evidence.
2. Run recognizable-object perception over that evidence and produce `perceived_objects`.
3. Establish a recognizable-memory record from the perceived objects. Preserve stable object identities and the evidence supporting each identity.
4. Merge the recognizable memory with the supplied ARC3 context and return the resulting `arc3_memory`.

## Acceptance requirements

The ARC3 context must augment the recognizable memory rather than replace it. Preserve the dependency from the original image through perceived objects to recognizable memory and finally to the bound ARC3 memory. Do not discard provenance, invent an image, or bind the memory to a context other than the supplied one.
