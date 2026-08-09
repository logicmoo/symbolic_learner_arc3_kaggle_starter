(
  (kind artifact_category)
  (id models.vision)
  (label "Vision Models")
  (description "Models and profiles declaring visual-input capability.")
  (path filtered/vision)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      model
    ))
    (where (
      (capabilities (
        (contains vision)
      ))
    ))
  ))
  (parentMode hide)
)
