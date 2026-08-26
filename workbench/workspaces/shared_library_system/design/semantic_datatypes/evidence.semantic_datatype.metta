(
  (kind semantic_datatype)
  (id evidence)
  (label Evidence)
  (description "Information that supports, contradicts, or qualifies a hypothesis, rule, or conclusion.")
  (specializations (
    (transition_evidence (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
