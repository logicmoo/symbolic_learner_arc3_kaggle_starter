(
  (kind backend)
  (id groq)
  (label "Groq Cloud")
  (provider groq)
  (official true)
  (description "Shared Groq OpenAI-compatible transport inherited by every workspace. Model files inherit this endpoint and add model-specific generation settings.")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.vision
  ))
  (configuration (
    (adapter openai_responses)
    (baseUrl https://api.groq.com/openai/v1)
    (apiKeyEnvironmentVariable GROQ_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_GROQ_BASE_URL)
    (legacyBaseUrlEnvironmentVariable ARC3_GROQ_BASE_URL)
    (defaultModel qwen/qwen3.6-27b)
    (modelEnvironmentVariable WORKBENCH_GROQ_MODEL)
    (legacyModelEnvironmentVariable ARC3_GROQ_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 600)
  ))
)
