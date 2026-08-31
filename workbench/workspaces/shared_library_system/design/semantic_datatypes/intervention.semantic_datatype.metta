(
  (kind semantic_datatype)
  (id intervention)
  (label Intervention)
  (description "A semantic action applied to an external or simulated world.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (human_intervention ())
  ))
  (inheritedBy (
    (human_intervention (
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
