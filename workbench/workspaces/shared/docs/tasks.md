# Tasks

A Task is the executable semantic operation in the workbench.

Tasks define what operation is being performed, its typed inputs and outputs, its implementation route, and—when the task uses an LLM—the model/profile dispatch policy and ordered prompt composition.

This is where the old ARC3 `llm_profiles[].prompt_text` list belongs. That list described the actual instruction package for a job, so it is task behavior rather than model configuration.

An LLM Task can therefore specify:

```text
model/profile selection
  single | parallel | compare | fallback

ordered prompts
  response_contract
  coordinate_contract
  object_extraction
  ...
```

The same Task can be run against several profiles without duplicating its prompt definition, and the same profile can be reused by unrelated Tasks.
