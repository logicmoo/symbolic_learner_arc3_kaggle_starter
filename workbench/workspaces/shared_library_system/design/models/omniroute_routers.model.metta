(
  (kind model)
  (id omniroute-free-router)
  (label "OmniRoute Best Free Router")
  (description "Uses OmniRoute's best-free route across the free providers connected to the local gateway.")
  (implements (
    (omniroute ())
  ))
  (model auto/best-free)
  (enabled true)
  (categories ([]
    models/omniroute
    models/routers
    models/free
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
  (dependsOn (
    (omniroute ())
  ))
  (dependedOnBy (
    (omniroute-free-router-preset-high ())
  ))
  (implementedBy (
    (omniroute-free-router-preset-high ())
  ))
  (inheritedBy (
    (omniroute-free-router-preset-high (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (inheritsFrom (
    (omniroute (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
