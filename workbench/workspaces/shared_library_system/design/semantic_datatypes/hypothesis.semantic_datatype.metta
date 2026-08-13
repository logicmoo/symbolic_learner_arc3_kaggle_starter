(
  (kind semantic_datatype)
  (id hypothesis)
  (label Hypothesis)
  (description "A revisable semantic explanation or candidate rule.")
  (runtimeContract (
    (shape map)
    (required ([]
      id
      statement
      confidence
    ))
    (properties (
      (id Text)
      (statement Text)
      (confidence Number)
      (supportingEvidence ([] TransitionEvidence))
      (contradictingEvidence ([] TransitionEvidence))
      (status Text)
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
