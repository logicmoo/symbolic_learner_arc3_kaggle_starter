(
  (kind atomspace)
  (id vision_analysis.default)
  (label "Default Vision Analysis AtomSpaces")
  (description "Binds the standard observation, model, rule, and goal AtomSpaces for a reusable visual-analysis loop.")
  (implements (
    (vision_analysis (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (atomspaces (
    (current_scene atomspace:current_scene)
    (world_model atomspace:world_model)
    (candidate_rules atomspace:candidate_rules)
    (goal_state atomspace:goal_state)
  ))
  (environment ())
  (parameters ())
)
