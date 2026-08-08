({}
  (kind model)
  (id openrouter-gpt-oss-20b)
  (label "gpt-oss-20b free")
  (description "Shared reasoning model migrated from the legacy LLM workflow catalog.")
  (inherits openrouter)
  (model openai/gpt-oss-20b:free)
  (enabled true)
  (capabilities (
    text
    reasoning
    json
  ))
  (metadata ({}
    (verifiedAvailable true)
    (verifiedAt 2026-08-04)
    (source "legacy config/llm_workflows.json")
  ))
)
