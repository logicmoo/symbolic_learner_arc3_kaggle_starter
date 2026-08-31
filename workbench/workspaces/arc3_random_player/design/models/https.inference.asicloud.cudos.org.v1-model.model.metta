(
  (kind model)
  (id https.inference.asicloud.cudos.org.v1-model)
  (label "ASICloud model")
  (implements (
    (https.inference.asicloud.cudos.org.v1 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (enabled false)
  (defaults (
    (temperature 0)
    (topP 1)
    (maxOutputTokens 12000)
    (reasoningEffort medium)
    (timeoutSeconds 300)
  ))
)
