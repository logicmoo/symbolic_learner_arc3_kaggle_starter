[← Back to top-level README](../../../../README.md)

# Models, Model Presets, Operations, and Prompts

The workbench keeps four concepts separate because they answer different questions.

## Backend

A backend is a root runtime/provider configuration. It describes **how to reach a capability**: API adapter, endpoint, credentials environment variables, executable, health check, and provider-level defaults. Backends live in the unified `models/` catalog and are identified by `kind: backend`.

## Model

A model inherits a backend and selects a concrete remote/local model. It describes **what model is being used** and may establish generation defaults.

## Model Preset

A Model Preset is a reusable specialization of a model. It describes **how we want to run a model**, but it does not contain prompts. A preset remains `kind model`; the UI recognizes it because its parent is another model rather than a backend. Presets may inherit other presets.

## Prompt

A prompt is reusable instruction text. Prompts live under `prompts/` and are edited independently of models and Model Presets. A Prompt Profile is a first-class ordered composition of Prompt IDs; it is selected by an Operation and is not a Model Preset.

## Operation

An Operation is the executable semantic operation. The old ARC3 `llm_profiles` records mixed model execution settings with a `prompt_text` list. The workbench splits those concerns: model execution settings become Model Presets; reusable ordered prompt lists become Prompt Profiles selected through an Operation implementation's `bindings.promptProfiles`.

```text
backend
  -> model
      -> model preset

prompt fragments -> prompt profile -----+
                                         |
operation -> chooses model/preset -------+--> LLM invocation
     -> chooses profiles/prompts --------+
```

The same Operation can run against several Model Presets without duplicating its prompts, and the same preset can be reused by unrelated Operations.

## ARC3 migration rule

For an old profile such as `openai-gpt-5.6-deep`, model/temperature/top-p/reasoning/token/timeout/image-detail fields become a prompt-free Model Preset. Its old `prompt_text` list becomes the ordered prompt composition of an ARC3 Operation.

The old light, deep, and extreme ARC3 prompt lists are therefore represented as Operations, while light/deep/extreme execution settings become Model Presets.

## ARC3 is not the reusable boundary

A large part of what was originally written for ARC3 is actually ordinary **vision and symbolic scene analysis** once the game-specific names are removed. Those pieces belong in `shared`.

Examples now treated as shared capabilities include:

- logical/source-image coordinate reasoning,
- semantic object extraction and topology preservation,
- visual reconstruction into executable Turtle programs,
- before/after transition observation,
- persistent-object correspondence across frames,
- evidence-based rule induction,
- symbolic artifact auditing and quality control.

ARC3 keeps only the contracts that genuinely depend on ARC3/debugger conventions, such as `object_registry.pl`, the exact ARC3 artifact filenames and response keys, and root-state behavior for the ARC3 action tree.

This means an ARC3 Operation is mostly a composition of shared vision prompts plus a small number of ARC3-local prompts. That is deliberate: the same visual learner should be reusable for games, UI understanding, scene tracking, robotics-style state observation, diagram analysis, and other image-to-symbol workflows.
