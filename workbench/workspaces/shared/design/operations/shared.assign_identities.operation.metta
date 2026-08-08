(
  (id shared.assign_identities)
  (label "Assign Stable Identities")
  (description "Assign stable symbolic identities to entities across views, states, or time. Generic symbolic perception operation.")
  (categories ([]
    vision/tracking
    symbolic/identity
    world-modeling/entities
  ))
  (implementation symbolic.identity)
  (inputs (
    (entities EntitySet)
  ))
  (outputs (
    (identities IdentityMap)
  ))
  (parameters ())
  (kind operation)
)
