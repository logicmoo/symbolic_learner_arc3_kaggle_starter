({}
  (kind goal)
  (id understand_visual_world)
  (label "Understand a Visual World")
  (description "Learn enough of a visual world's objects and dynamics to explain changes and pursue a desired state.")
  (successCriteria (
    "Explain observed state transitions"
    "Preserve evidence for every inferred rule and chosen action"
  ))
  (metadata ({}
    (domain vision)
    (shared true)
  ))
  (children (
    understand_visual_world.explore_safely
    understand_visual_world.explain_dynamics
  ))
  (preferredChild understand_visual_world.explain_dynamics)
)
