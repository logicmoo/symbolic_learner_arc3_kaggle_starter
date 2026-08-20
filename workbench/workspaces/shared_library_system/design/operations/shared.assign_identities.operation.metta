(
  (id shared.assign_identities)
  (label "Assign Stable Identities")
  (description "Assign stable symbolic identities to entities across views, states, or time. Generic symbolic perception operation.")
  (topics ([]
    vision
    symbolic
    object-identity
    world-modeling
  ))
  (implementation symbolic.identity)
  (inputs (
    (entities EntityCollection)
  ))
  (outputs (
    (identities IdentityMap)
  ))
  (parameters ())
  (kind operation)
)
