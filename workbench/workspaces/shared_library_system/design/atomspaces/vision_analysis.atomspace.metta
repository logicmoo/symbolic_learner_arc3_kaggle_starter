(
  (kind atomspace)
  (id vision_analysis)
  (label "Vision Analysis AtomSpaces")
  (description "Declares the AtomSpaces and runtime bindings available while observing, explaining, and acting in a visual world.")
  (specializations (
    (vision_analysis.default (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization vision_analysis.default)
  (bindings ([]
    current_scene
    world_model
    candidate_rules
    goal_state
  ))
)
