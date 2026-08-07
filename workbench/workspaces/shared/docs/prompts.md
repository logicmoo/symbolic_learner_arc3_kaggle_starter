[← Back to top-level README](../../../../README.md)

# Prompts

Prompts are reusable instruction fragments stored under `prompts/`.

A Prompt has an ID, label, optional variables/metadata, and text. It does not choose a model and it does not decide when it runs.

Operations select and order Prompt IDs in `promptSelection` to build the instruction package for an LLM invocation. This makes prompt text independently editable and reusable across models, profiles, operations, and workspaces.

## Shared vision prompts

Much of the original ARC3 prompt package is now shared because it is really visual/symbolic perception rather than game-specific logic. Examples include:

```text
logical_image_coordinates
object_extraction
symbolic_scene_fact_schema
turtle_reconstruction
turtle_motion_dsl
transition_observation
object_correspondence
rule_hypothesis
symbolic_rule_evidence_schema
output_quality_control
```

These can be reused by non-ARC image workflows.

## ARC3-local prompts

Only the contracts that depend on the ARC3 debugger remain in `arc3/prompts/`, including:

```text
arc3_response_contract
arc3_identity_registry
arc3_file_separation
arc3_root_state
```

An ARC3 Operation therefore composes shared visual prompts with a small ARC3-specific layer.

## Old `prompt_text`

The legacy `llm_profiles[].prompt_text` arrays are no longer profile fields. Their ordering is represented on the Operation as `promptSelection.prompts`. A profile can change temperature or reasoning effort without silently changing the job instructions.
