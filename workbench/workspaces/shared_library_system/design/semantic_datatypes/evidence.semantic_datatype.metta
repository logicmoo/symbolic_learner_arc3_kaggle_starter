(
  (kind semantic_datatype)
  (id evidence)
  (label Evidence)
  (description "Information that supports, contradicts, or qualifies a hypothesis, rule, or conclusion.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (transition_evidence ())
  ))
  (inheritedBy (
    (transition_evidence (
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
