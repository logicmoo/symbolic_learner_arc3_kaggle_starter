(
  (kind backend)
  (id asicloud)
  (label ASICloud)
  (provider asicloud)
  (official true)
  (description "ASI Alliance OpenAI-compatible inference transport for MiniMax models hosted by ASICloud on CUDOS.")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.tools
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl https://inference.asicloud.cudos.org/v1)
    (apiKeyEnvironmentVariable ASI_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_ASICLOUD_BASE_URL)
    (modelEnvironmentVariable WORKBENCH_ASICLOUD_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 900)
  ))
)
