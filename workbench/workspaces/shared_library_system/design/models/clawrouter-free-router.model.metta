(
  (kind model)
  (id clawrouter-free-router)
  (label "ClawRouter Free Models Router")
  (description "Routes requests through the local ClawRouter proxy to a free capable model without an API key or funded wallet.")
  (model blockrun/free)
  (enabled true)
  (categories ([]
    models/clawrouter
    models/routers
    models/free
    filtered/free
    filtered/vision
  ))
  (capabilities ([]
    text
    vision
    reasoning
    json
    tools
  ))
  (properties (
    (router true)
    (free true)
    (localProxy true)
  ))
  (implements (
    (clawrouter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
