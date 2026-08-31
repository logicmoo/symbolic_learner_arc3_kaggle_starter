(
  (kind model)
  (id asicloud-asi1)
  (label asi1)
  (description "Discovered from ASICloud.")
  (implements (
    (https.inference.asicloud.cudos.org.v1 ())
  ))
  (model asi1)
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
    (id asi1)
    (owned_by snet+cudo)
    (object model)
    (created 0)
    (ownedBy snet+cudo)
  ))
  (providerMetadata (
    (id asi1)
    (owned_by snet+cudo)
    (object model)
    (created 0)
  ))
  (discovery (
    (managed true)
    (backendId https.inference.asicloud.cudos.org.v1)
    (remoteModelId asi1)
  ))
  (categories ([]
    filtered/asi1
    filtered/vision
    models
    reasoning
    todo-needs-categorization
    vision
  ))
  (sources ([]
    lookup:unresolved
  ))
  (notes "No reliable public capability metadata found during this pass; keep backend-declared values until curated evidence is added.")
  (dependsOn (
    (https.inference.asicloud.cudos.org.v1 ())
  ))
  (inheritsFrom (
    (https.inference.asicloud.cudos.org.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
