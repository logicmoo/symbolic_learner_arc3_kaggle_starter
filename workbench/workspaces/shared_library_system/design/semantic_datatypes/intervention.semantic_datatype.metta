(
  (kind semantic_datatype)
  (id intervention)
  (label Intervention)
  (description "A semantic action applied to an external or simulated world.")
  (specializations (
    (human_intervention (
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
