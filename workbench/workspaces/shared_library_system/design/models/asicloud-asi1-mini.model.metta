(
  (kind model)
  (id asicloud-asi1-mini)
  (label "Free asi1-mini")
  (description "Discovered from ASICloud.")
  (implements (
    (https.inference.asicloud.cudos.org.v1 ())
  ))
  (model asi1-mini)
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
    (backendId https.inference.asicloud.cudos.org.v1)
    (remoteModelId asi1-mini)
  ))
  (categories ([]
    filtered/vision
  ))
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
