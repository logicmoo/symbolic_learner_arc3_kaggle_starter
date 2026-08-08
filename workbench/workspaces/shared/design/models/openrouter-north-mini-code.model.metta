(
  (kind model)
  (id openrouter-north-mini-code)
  (label "North Mini Code free")
  (description "Shared code/reasoning model migrated from the legacy LLM workflow catalog.")
  (inherits openrouter)
  (model cohere/north-mini-code:free)
  (enabled true)
  (capabilities ([]
    text
    reasoning
    code
    json
  ))
  (metadata (
    (verifiedAvailable true)
    (verifiedAt 2026-08-04)
    (source "legacy config/llm_workflows.json")
  ))
)
