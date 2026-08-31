(
  (kind model)
  (id omniroute-free-router-preset-high)
  (label "OmniRoute Best Free Router Preset High")
  (implements (
    (omniroute-free-router ())
  ))
  (enabled true)
  (defaults (
    (temperature 0.2)
    (topP 1)
    (maxOutputTokens 12000)
    (reasoningEffort medium)
    (timeoutSeconds 300)
    (parentImageDetail high)
  ))
  (categories ([]
    filtered/free
  ))
  (dependsOn (
    (omniroute-free-router ())
  ))
  (inheritsFrom (
    (omniroute-free-router (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
