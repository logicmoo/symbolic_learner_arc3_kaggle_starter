(
  (kind representation_datatype)
  (id bitmap)
  (label "Bitmap Image")
  (implements (
    (image ())
  ))
  (implementedBy (
    (png ())
    (jpeg ())
    (bmp ())
  ))
  (inheritedBy (
    (png (
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
    (jpeg (
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
    (bmp (
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
  (preferredImplementation png)
  (inheritsFrom (
    (image (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
