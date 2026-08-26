(
  (kind representation_datatype)
  (id plain_text)
  (label "Plain Text")
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (text (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (specializations (
    (utf8_text (
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
    (markdown (
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
  (preferredSpecialization utf8_text)
)
