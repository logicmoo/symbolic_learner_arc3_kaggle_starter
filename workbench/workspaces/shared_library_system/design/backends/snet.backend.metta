(
  (kind backend)
  (id https.llm.c.singularitynet.io.v1)
  (aliases ([]
    snet
    singularitynet
    singularitynet-llm
    https://llm.c.singularitynet.io/v1
  ))
  (label "SingularityNET LLM")
  (provider singularitynet)
  (official true)
  (description "SingularityNET OpenAI-compatible LLM transport. Model resources inherit this backend and provide their provider model identifiers.")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.tools
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl https://llm.c.singularitynet.io/v1)
    (apiKeyEnvironmentVariable SNET_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_SNET_BASE_URL)
    (modelEnvironmentVariable WORKBENCH_SNET_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 900)
  ))
)
