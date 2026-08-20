(
  (kind artifact_category)
  (id subjects.segmentation)
  (label "Segmentation")
  (description "Operations that partition an observation into candidate entities or connected components. A subject matter an operation participates in, independent of whether the input is visual and of how the operation executes.")
  (path subjects/segmentation)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (subjects (
        (contains segmentation)
      ))
    ))
  ))
  (parentMode show)
)
