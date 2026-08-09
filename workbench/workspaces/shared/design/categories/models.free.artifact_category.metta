(
  (kind artifact_category)
  (id models.free)
  (label "Free Models")
  (description "Models with Free Usability.")
  (path filtered/free)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      model
    ))
    (where (
      (id (
        (contains free)
      ))
    ))
  ))
  (parentMode hide)
)
