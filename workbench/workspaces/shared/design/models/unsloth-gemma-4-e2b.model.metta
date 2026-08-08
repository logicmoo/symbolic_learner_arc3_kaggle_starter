(
  (kind model)
  (id unsloth-gemma-4-e2b)
  (label "Gemma 4 E2B local")
  (description "Local Gemma model inheriting the shared Unsloth Studio backend catalog item.")
  (inherits unsloth)
  (model unsloth/gemma-4-E2B-it-GGUF)
  (enabled true)
  (capabilities ([]
    text
    vision
    json
    local
  ))
  (defaults (
    (reasoningEffort medium)
    (maxOutputTokens 12000)
    (temperature 0.05)
    (topP 0.95)
    (timeoutSeconds 600)
    (currentImageDetail high)
    (parentImageDetail low)
  ))
)
