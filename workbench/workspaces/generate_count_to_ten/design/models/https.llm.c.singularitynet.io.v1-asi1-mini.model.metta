(
  (kind model)
  (id https.llm.c.singularitynet.io.v1-asi1-mini)
  (label asi1-mini)
  (description "Discovered from SingularityNET LLM.")
  (implements (
    (https.llm.c.singularitynet.io.v1 ())
  ))
  (model asi1-mini)
  (enabled false)
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
    (id asi1-mini)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id asi1-mini)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId asi1-mini)
  ))
  (categories ([]
    filtered/vision
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
