({}
  (kind model)
  (id qwen-3.6-27b-groq)
  (label "Qwen 3.6 27B on Groq")
  (description "Fast Qwen model inheriting the shared Groq backend catalog item.")
  (inherits groq)
  (model qwen/qwen3.6-27b)
  (enabled true)
  (capabilities (
    text
    vision
    json
  ))
  (defaults ({}
    (reasoningEffort medium)
    (maxOutputTokens 12000)
    (temperature 0.05)
    (topP 0.95)
    (timeoutSeconds 300)
    (currentImageDetail high)
    (parentImageDetail low)
  ))
  (environment ({}
    (model WORKBENCH_GROQ_MODEL)
    (legacyModel ARC3_GROQ_MODEL)
  ))
)
