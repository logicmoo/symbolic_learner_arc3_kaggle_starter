(
  (kind representation_datatype)
  (id object_list)
  (label "Object List")
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
    (prolog_facts (
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
