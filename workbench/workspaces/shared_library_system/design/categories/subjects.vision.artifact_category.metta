(
  (kind artifact_category)
  (id subjects.vision)
  (label "Vision")
  (description "Operations whose subject matter is visual perception: they reason over images or visual states. Separate from segmentation, which an operation may participate in without being visual.")
  (path subjects/vision)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (subjects (
        (contains vision)
      ))
    ))
  ))
  (parentMode show)
)
