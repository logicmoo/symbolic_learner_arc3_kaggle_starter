(
  (kind representation_datatype)
  (id prolog_fact_set)
  (label "Prolog Fact Set")
  (language prolog)
  (implements (
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
  (specializations (
    (prolog_source (
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
  (preferredSpecialization prolog_source)
)
