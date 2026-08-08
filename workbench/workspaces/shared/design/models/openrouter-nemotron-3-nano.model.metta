({}
  (kind model)
  (id openrouter-nemotron-3-nano)
  (label "Nemotron 3 Nano 30B A3B free")
  (description "Shared reasoning model migrated from the legacy LLM workflow catalog.")
  (inherits openrouter)
  (model nvidia/nemotron-3-nano-30b-a3b:free)
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
