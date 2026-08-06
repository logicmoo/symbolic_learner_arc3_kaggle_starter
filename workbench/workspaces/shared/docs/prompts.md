# Prompts

Prompts are reusable instruction fragments stored under `prompts/`.

A Prompt has an ID, label, optional variables/metadata, and text. It does not choose a model and it does not decide when it runs.

Tasks select and order Prompt IDs to build the instruction package for an LLM invocation. This makes prompt text independently editable and reusable across models, profiles, tasks, and workspaces.

For example, ARC-style analysis might compose:

```text
response_contract
coordinate_contract
identity_contract
object_extraction
turtle_reconstruction
transitions
quality_control
```

A different task can reuse only the fragments it needs. Changing a model profile therefore changes execution behavior without implicitly changing the prompt content.
