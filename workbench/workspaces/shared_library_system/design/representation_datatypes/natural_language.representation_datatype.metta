(
  (kind representation_datatype)
  (id natural_language)
  (label "Natural-Language Description")
  (language natural_language)
  (implements (
    (image ())
    (text ())
  ))
  (implementedBy (
    (markdown ())
    (text_plain ())
  ))
  (inheritedBy (
    (markdown (
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
    (text_plain (
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
  (preferredImplementation markdown)
  (inheritsFrom (
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
)
