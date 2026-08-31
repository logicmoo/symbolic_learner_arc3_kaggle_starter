(
  (kind semantic_datatype)
  (id relationship)
  (label Relationship)
  (description "A semantic relationship between entities or other information objects.")
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
