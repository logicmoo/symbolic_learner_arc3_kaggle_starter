(
  (kind semantic_datatype)
  (id evaluation)
  (label Evaluation)
  (description "A semantic assessment, score, validation result, or comparison.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (prolog_fact_set ())
    (system_readiness ())
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
    (system_readiness (
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
