(
  (kind semantic_datatype)
  (id object)
  (label Object)
  (description "A structured symbolic value independent of its in-memory or serialized representation.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (json_object ())
    (python_object ())
  ))
  (inheritedBy (
    (json_object (
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
    (python_object (
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
  (preferredImplementation json_object)
  (inheritsFrom (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
