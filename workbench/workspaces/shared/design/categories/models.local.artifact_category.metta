(
  (kind artifact_category)
  (id models.local)
  (label "Local Models")
  (description "Models resolved through the local Unsloth Studio backend.")
  (path filtered/models/local)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      model
      profile
    ))
    (where (
      (_resolved.backendId (
        (equals unsloth)
      ))
    ))
  ))
  (parentMode show)
)
