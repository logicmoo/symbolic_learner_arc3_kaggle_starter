(
  (kind backend)
  (id openai)
  (label OpenAI)
  (provider openai)
  (official true)
  (description "Shared OpenAI-compatible backend used as the root of the visible model/profile inheritance example.")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.vision
    llm
    vision
    reasoning
  ))
  (configuration (
    (adapter openai_responses)
    (baseUrl https://api.openai.com/v1)
    (apiKeyEnvironmentVariable OPENAI_API_KEY)
    (defaultModel gpt-5.6)
    (modelEnvironmentVariable WORKBENCH_OPENAI_MODEL)
    (legacyModelEnvironmentVariable ARC3_OPENAI_MODEL)
    (defaultAnalysisLevel 4)
    (timeoutSeconds 900)
    (apiKeyEnvironment OPENAI_API_KEY)
  ))
  (modelDefaults (
    (temperature 0)
    (topP 1)
    (maxOutputTokens 12000)
    (reasoningEffort medium)
    (timeoutSeconds 300)
  ))
)
