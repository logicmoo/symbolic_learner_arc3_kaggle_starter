[← Back to top-level README](../../../../README.md)

# Prompts

Prompts are reusable instruction fragments stored under `prompts/`.

A Prompt has an ID, label, optional variables/metadata, and text. It does not choose a model and it does not decide when it runs.

Operation implementations bind Prompt Profiles and/or individual Prompt IDs in `bindings` to build the instruction package for an LLM invocation. This makes prompt text independently editable and reusable across models, Model Presets, operations, and workspaces.

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

The legacy `llm_profiles[].prompt_text` arrays are no longer model-configuration fields. Reusable ordered compositions are `kind prompt_profile` resources; an Operation implementation binds them with `bindings.promptProfiles` and may append individual prompts with `bindings.prompts`. A Model Preset can change temperature or reasoning effort without silently changing the job instructions.

## Prompt Profiles

A Prompt Profile is an ordered, reusable composition—not a model configuration and not a prompt alternative. Profiles live beside prompts under `design/prompts/`, declare `kind prompt_profile`, list semantic Prompt IDs in `prompts`, and define the separator used within that composition. The shared library includes Object-First and Scene-Graph examples. The Prompts editor can create, reorder, edit, enable, and save profiles; LLM Operation implementations select them independently of models and Model Presets.
