(
  (kind artifact_category)
  (id filtered.prolog)
  (label "Prolog Implementations")
  (description "Operations implemented through SWI-Prolog or another Prolog source route.")
  (path filtered/prolog)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation_implementation
    ))
    (where (
      (implementation (
        (startsWith prolog)
      ))
    ))
  ))
  (parentMode show)
)
