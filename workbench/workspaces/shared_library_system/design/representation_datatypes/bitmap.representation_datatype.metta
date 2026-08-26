(
  (kind representation_datatype)
  (id bitmap)
  (label "Bitmap Image")
  (implements (
    (image (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (specializations (
    (png (
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
    (jpeg (
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
    (bmp (
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
  (preferredSpecialization png)
)
