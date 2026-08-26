(
  (kind representation_datatype)
  (id natural_language)
  (label "Natural-Language Description")
  (language natural_language)
  (implements (
    (image (
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
    (text_plain (
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
  (preferredSpecialization markdown)
)
