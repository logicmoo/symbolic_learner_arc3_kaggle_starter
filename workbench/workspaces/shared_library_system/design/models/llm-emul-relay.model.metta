(
  (kind model)
  (id llm-emul-relay)
  (label "LLM Emulator Relay")
  (description "Not a real model process -- every request is relayed over the /llm_emul WebSocket to whichever worker (human or agent) is currently connected, per scripts/llm_emul_worker.py. Returns 503 if no worker is connected, 504 if none replies in time.")
  (model llm-emul)
  (enabled true)
  (categories ([]
    models/llm_emul
    models/local
  ))
  (capabilities ([]
    text
    reasoning
  ))
  (properties (
    (localProxy true)
    (humanInTheLoop true)
  ))
  (parents ([]
    llm_emul
  ))
)
