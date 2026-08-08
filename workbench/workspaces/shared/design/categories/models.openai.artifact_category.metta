({}
  (kind artifact_category)
  (id models.openai)
  (label "OpenAI Backend")
  (description "The OpenAI backend and its inherited model/profile hierarchy.")
  (path filtered/models/providers/openai)
  (trees (
    models
  ))
  (query ({}
    (kinds (
      backend
    ))
    (where ({}
      (provider ({}
        (equals openai)
      ))
    ))
  ))
  (parentMode user)
)
