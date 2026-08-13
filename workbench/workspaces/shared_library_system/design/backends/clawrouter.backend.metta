(
  (kind backend)
  (id clawrouter)
  (label ClawRouter)
  (provider clawrouter)
  (official true)
  (description "Local-first ClawRouter OpenAI-compatible gateway. run_workbench.bat starts its keyless proxy on port 3456; the default blockrun/free route requires no wallet balance.")
  (enabled true)
  (children ([]
    clawrouter-free-router
  ))
  (capabilities ([] llm.complete llm.reasoning llm.vision))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl http://127.0.0.1:3456/v1)
    (defaultModel blockrun/free)
    (timeoutSeconds 900)
  ))
)
