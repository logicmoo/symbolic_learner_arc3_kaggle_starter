(
  (kind model)
  (id snet-asi1)
  (label "SingularityNET asi1")
  (description "The asi1 model served by the SingularityNET OpenAI-compatible LLM backend.")
  (implements (
    (https.llm.c.singularitynet.io.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (model asi1)
  (enabled true)
  (capabilities (
    (text true)
    (audio false)
    (vision false)
    (reasoning false)
    (tools false)
    (json false)
  ))
  (limits (
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (discovery (
    (managed true)
    (backendId https.llm.c.singularitynet.io.v1)
    (remoteModelId asi1)
  ))
  (categories ([]
    models/singularitynet
  ))
)
