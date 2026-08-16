(
  (kind model)
  (id openrouter-body-builder)
  (label "OpenRouter Body Builder")
  (description "Transforms natural-language requests into structured OpenRouter API request bodies for tasks that may run across multiple models in parallel.")
  (model openrouter/bodybuilder)
  (enabled false)
  (categories ([]
    models/openrouter
    models/routers
  ))
  (capabilities ([]
    text
    json
    tools
  ))
  (properties (
    (router true)
  ))
  (parents ([]
    openrouter
  ))
)
