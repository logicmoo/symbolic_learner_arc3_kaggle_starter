(
  (kind backend)
  (id prolog)
  (label "SWI-Prolog Runtime")
  (provider prolog)
  (description "Executes Prolog programs and queries through SWI-Prolog.")
  (enabled true)
  (capabilities ([]
    prolog.query
  ))
  (configuration (
    (executable swipl)
    (arguments ([]
      -q
    ))
    (timeoutSeconds 300)
  ))
)
