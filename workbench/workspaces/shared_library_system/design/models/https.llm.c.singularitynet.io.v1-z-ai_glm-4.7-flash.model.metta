(
  (kind model)
  (id https.llm.c.singularitynet.io.v1-z-ai_glm-4.7-flash)
  (label z-ai/glm-4.7-flash)
  (description "Discovered from SingularityNET LLM.")
  (implements (
    (https.llm.c.singularitynet.io.v1 ())
  ))
  (model z-ai/glm-4.7-flash)
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
    (id z-ai/glm-4.7-flash)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id z-ai/glm-4.7-flash)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId z-ai/glm-4.7-flash)
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
