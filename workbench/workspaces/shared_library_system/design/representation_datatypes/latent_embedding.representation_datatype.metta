(
  (kind representation_datatype)
  (id latent_embedding)
  (label "Latent Embedding")
  (implements (
    (image ())
  ))
  (implementedBy (
    (vector_json ())
    (numpy ())
  ))
  (inheritedBy (
    (vector_json (
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
    (numpy (
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
  (preferredImplementation vector_json)
  (inheritsFrom (
    (image (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
