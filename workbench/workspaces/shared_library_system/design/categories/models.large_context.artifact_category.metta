(
  (kind artifact_category)
  (id models.large_context)
  (label "Large Context Models")
  (description "Models whose imported provider metadata advertises at least a 100K-token context window.")
  (path filtered/large-context)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      model
    ))
    (where (
      (properties.context_length (
        (gte 100000)
      ))
    ))
  ))
  (parentMode hide)
)
