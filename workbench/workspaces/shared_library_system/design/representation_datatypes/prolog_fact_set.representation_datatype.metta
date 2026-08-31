(
  (kind representation_datatype)
  (id prolog_fact_set)
  (label "Prolog Fact Set")
  (language prolog)
  (implements (
    (information ())
    (entity_collection ())
    (relationship ())
    (world_state ())
    (world_model ())
    (transition_evidence ())
    (hypothesis ())
    (evaluation ())
  ))
  (implementedBy (
    (prolog_source ())
  ))
  (inheritedBy (
    (prolog_source (
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
  (preferredImplementation prolog_source)
  (inheritsFrom (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (entity_collection (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (relationship (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (world_state (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (world_model (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (transition_evidence (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (hypothesis (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (evaluation (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
