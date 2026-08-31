(
  (kind semantic_datatype)
  (id text)
  (label Text)
  (description "Textual information independent of language, markup, file encoding, or model-oriented prompt representation.")
  (implements (
    (information ())
  ))
  (implementedBy (
    (natural_language ())
    (plain_text ())
  ))
  (inheritedBy (
    (natural_language (
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
    (plain_text (
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
  (preferredImplementation plain_text)
  (inheritsFrom (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
