(
  (kind profile)
  (id gpt-5.6-fast)
  (label "GPT-5.6 / Fast")
  (description "Lower-latency GPT-5.6 profile for routine workbench steps.")
  (inherits gpt-5.6)
  (enabled true)
  (defaults (
    (reasoningEffort low)
    (analysisLevel 0)
    (maxOutputTokens 8000)
    (timeoutSeconds 120)
  ))
)
