(
  (kind backend)
  (id llm_emul)
  (label "LLM Emulator (agent relay)")
  (provider llm_emul)
  (official true)
  (description "Simulated LLM backend: relays chat-completion requests over a WebSocket (/llm_emul) to whichever agent/human worker is currently connected (see scripts/llm_emul_worker.py). No API key or real model process required -- just start the worker script and it answers requests as they arrive.")
  (enabled true)
  (children ([]
    llm-emul-relay
  ))
  (capabilities ([] llm.complete llm.reasoning))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl http://127.0.0.1:8000/v1)
    (defaultModel llm-emul)
    (timeoutSeconds 900)
  ))
)
