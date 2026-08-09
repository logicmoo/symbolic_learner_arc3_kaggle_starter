(
  (id shared.derive_properties)
  (label "Derive Symbolic Properties")
  (description "Derive grounded properties and relations for identified entities. Generic symbolic-analysis operation.")
  (categories ([]
    symbolic/properties
    world-modeling/entities
    vision/recognition
  ))
  (implementation prolog.properties)
  (inputs (
    (identities IdentityMap)
  ))
  (outputs (
    (facts (
      (datatype entity_collection)
      (representation symbolic_fact_set)
    ))
  ))
  (parameters ())
  (kind operation)
)
