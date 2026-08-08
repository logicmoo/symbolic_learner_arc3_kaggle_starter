({}
  (kind model)
  (id openrouter-gemma-4-26b-a4b)
  (label "Gemma 4 26B A4B free")
  (description "Shared vision-capable model migrated from the legacy LLM workflow catalog.")
  (inherits openrouter)
  (model google/gemma-4-26b-a4b-it:free)
  (enabled true)
  (capabilities (
    text
    vision
    reasoning
    json
  ))
  (metadata ({}
    (verifiedAvailable true)
    (verifiedAt 2026-08-04)
    (source "legacy config/llm_workflows.json")
  ))
)
