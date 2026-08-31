(
  (kind semantic_datatype)
  (id world_model)
  (label "World Model")
  (description "A revisable semantic model of entities, state, dynamics, constraints, evidence, and uncertainty.")
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
