(
  (kind semantic_datatype)
  (id transition_evidence)
  (label "Transition Evidence")
  (description "Evidence about how a world changed between observations.")
  (runtimeContract (
    (shape map)
    (required ([]
      id
      observation
    ))
    (properties (
      (id Text)
      (observation Text)
      (supports ([] Text))
      (contradicts ([] Text))
      (confidence Number)
      (artifactRefs ([] Text))
    ))
  ))
  (children ([]
    prolog_fact_set
    symbolic_fact_set
  ))
  (parents ([]
    information
  ))
)
