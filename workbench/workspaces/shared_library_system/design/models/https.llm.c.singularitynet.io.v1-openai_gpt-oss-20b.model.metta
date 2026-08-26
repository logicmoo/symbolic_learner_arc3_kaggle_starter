(
  (kind model)
  (id https.llm.c.singularitynet.io.v1-openai_gpt-oss-20b)
  (label openai/gpt-oss-20b)
  (description "Discovered from SingularityNET LLM.")
  (implements (
    (https.llm.c.singularitynet.io.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (model openai/gpt-oss-20b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id openai/gpt-oss-20b)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id openai/gpt-oss-20b)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId openai/gpt-oss-20b)
  ))
)
