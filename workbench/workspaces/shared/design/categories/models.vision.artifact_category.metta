({}
  (kind artifact_category)
  (id models.vision)
  (label "Vision Models")
  (description "Models and profiles declaring visual-input capability.")
  (path filtered/models/vision)
  (trees (
    models
  ))
  (query ({}
    (kinds (
      model
      profile
    ))
    (where ({}
      (capabilities ({}
        (contains vision)
      ))
    ))
  ))
  (parentMode show)
)
