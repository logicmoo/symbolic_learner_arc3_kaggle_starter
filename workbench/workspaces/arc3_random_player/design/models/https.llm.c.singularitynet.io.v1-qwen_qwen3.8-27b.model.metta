(
  (kind model)
  (id https.llm.c.singularitynet.io.v1-qwen_qwen3.8-27b)
  (label qwen/qwen3.8-27b)
  (description "Discovered from SingularityNET LLM.")
  (implements (
    (https.llm.c.singularitynet.io.v1 ())
  ))
  (model qwen/qwen3.8-27b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id qwen/qwen3.8-27b)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id qwen/qwen3.8-27b)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId qwen/qwen3.8-27b)
  ))
  (dependsOn (
    (https.llm.c.singularitynet.io.v1 ())
  ))
  (inheritsFrom (
    (https.llm.c.singularitynet.io.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
