(
  (kind artifact_category)
  (id backends.category)
  (label "All Backends")
  (description "All backend resources available to the model catalog.")
  (path backends)
  (icon "fa-solid/database")
  (color "color-for-kind:artifact_category")
  (order 1000)
  (visible "(eq (workspace-kind) backend)")
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
    ))
    (where (
      (kind (
        (startsWith backend)
      ))
    ))
  ))
  (parentMode hide)
)
