(
  (kind semantic_datatype)
  (id text)
  (label Text)
  (description "Textual information independent of language, markup, file encoding, or model-oriented prompt representation.")
  (specializations (
    (natural_language (
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
    (plain_text (
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
  (preferredSpecialization plain_text)
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
