(
  (kind model)
  (id https.llm.c.singularitynet.io.v1-google_gemma-4-31b-it)
  (label google/gemma-4-31b-it)
  (description "Discovered from SingularityNET LLM.")
  (implements (
    (https.llm.c.singularitynet.io.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (model google/gemma-4-31b-it)
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
    (id google/gemma-4-31b-it)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id google/gemma-4-31b-it)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId google/gemma-4-31b-it)
  ))
)
