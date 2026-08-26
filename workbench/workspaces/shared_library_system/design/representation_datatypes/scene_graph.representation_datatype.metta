(
  (kind representation_datatype)
  (id scene_graph)
  (label "Scene Graph")
  (implements (
    (image (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (specializations (
    (json (
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
  (preferredSpecialization json)
)
