(
  (kind atomspace)
  (id vision_analysis)
  (label "Vision Analysis AtomSpaces")
  (description "Declares the AtomSpaces and runtime bindings available while observing, explaining, and acting in a visual world.")
  (bindings ([]
    current_scene
    world_model
    candidate_rules
    goal_state
  ))
  (implementedBy (
    (vision_analysis.default ())
  ))
  (inheritedBy (
    (vision_analysis.default (
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
  (preferredImplementation vision_analysis.default)
)
