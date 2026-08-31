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
      (supportingEvidence ([]
        TransitionEvidence
      ))
      (contradictingEvidence ([]
        TransitionEvidence
      ))
      (status Text)
    ))
  ))
  (implements (
    (information ())
  ))
  (implementedBy (
    (prolog_fact_set ())
    (symbolic_fact_set ())
  ))
  (inheritedBy (
    (prolog_fact_set (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (symbolic_fact_set (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (inheritsFrom (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
