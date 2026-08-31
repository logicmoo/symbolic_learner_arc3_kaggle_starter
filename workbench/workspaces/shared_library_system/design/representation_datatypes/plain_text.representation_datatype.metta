(
  (kind representation_datatype)
  (id plain_text)
  (label "Plain Text")
  (implements (
    (information ())
    (text ())
  ))
  (implementedBy (
    (utf8_text ())
    (markdown ())
  ))
  (inheritedBy (
    (utf8_text (
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
  ))
  (preferredImplementation utf8_text)
  (inheritsFrom (
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
)
