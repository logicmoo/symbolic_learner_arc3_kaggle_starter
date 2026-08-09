(
  (kind artifact_category)
  (id filtered.prolog)
  (label "Prolog References")
  (description "Uses implemented through SWI-Prolog or another Prolog source route.")
  (path filtered/prolog)
  (trees ([]
    operations
    prompts
  ))
  (query (
    (kinds ([]
      operation
      prompt
    ))
    (where (
      (implementation (
        (startsWith prolog)
      ))
    ))
  ))
  (parentMode show)
)
