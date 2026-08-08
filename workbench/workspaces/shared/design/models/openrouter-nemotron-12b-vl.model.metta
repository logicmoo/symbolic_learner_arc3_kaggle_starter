({}
  (kind model)
  (id openrouter-nemotron-12b-vl)
  (label "Nemotron Nano 12B 2 VL free")
  (description "Vision-language Nemotron model inheriting the shared OpenRouter backend catalog item.")
  (inherits openrouter)
  (model nvidia/nemotron-nano-12b-v2-vl:free)
  (enabled true)
  (capabilities (
    text
    vision
    json
  ))
  (defaults ({}
    (reasoningEffort medium)
    (maxOutputTokens 14000)
    (temperature 0.05)
    (topP 0.95)
    (timeoutSeconds 420)
    (currentImageDetail high)
    (parentImageDetail low)
  ))
)
