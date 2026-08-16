(
  (kind backend)
  (id https.api.asi1.ai.v1)
  (aliases ([]
    asione
    asi-one
    asi1
    https://api.asi1.ai/v1
  ))
  (label ASI:One)
  (provider asione)
  (official true)
  (description "ASI:One OpenAI-compatible inference transport for the ASI1 model family, including ASI1 Ultra.")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.tools
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl https://api.asi1.ai/v1)
    (apiKeyEnvironmentVariable ASIONE_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_ASIONE_BASE_URL)
    (defaultModel asi1-ultra)
    (modelEnvironmentVariable WORKBENCH_ASIONE_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 900)
  ))
)
