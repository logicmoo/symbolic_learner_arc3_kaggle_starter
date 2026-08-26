(
  (kind semantic_datatype)
  (id object)
  (label Object)
  (description "A structured symbolic value independent of its in-memory or serialized representation.")
  (specializations (
    (json_object (
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
    (python_object (
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
  (preferredSpecialization json_object)
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
