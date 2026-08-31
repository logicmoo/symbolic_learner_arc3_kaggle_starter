(
  (kind semantic_datatype)
  (id program)
  (label Program)
  (description "Executable or interpretable instructions independent of their source language and storage representation.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (prolog_program ())
    (turtle_program_set ())
  ))
  (inheritedBy (
    (prolog_program (
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
    (turtle_program_set (
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
