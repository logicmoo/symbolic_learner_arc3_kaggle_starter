(
  (kind semantic_datatype)
  (id observation)
  (label Observation)
  (description "Evidence received from an external world, independent of how that evidence is represented.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (objectified_observation ())
  ))
  (inheritedBy (
    (objectified_observation (
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
