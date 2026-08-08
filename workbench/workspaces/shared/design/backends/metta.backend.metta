(
  (kind backend)
  (id metta)
  (label "MeTTa Runtime")
  (provider metta)
  (description "Evaluates MeTTa expressions through the configured MeTTa executable.")
  (enabled true)
  (capabilities ([]
    metta.evaluate
  ))
  (configuration (
    (executable metta)
    (timeoutSeconds 300)
  ))
)
