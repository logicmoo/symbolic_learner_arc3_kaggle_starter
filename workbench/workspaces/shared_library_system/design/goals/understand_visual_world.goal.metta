(
  (kind goal)
  (id understand_visual_world)
  (label "Understand a Visual World")
  (description "Learn enough of a visual world's objects and dynamics to explain changes and pursue a desired state.")
  (successCriteria ([]
    "Explain observed state transitions"
    "Preserve evidence for every inferred rule and chosen action"
  ))
  (metadata (
    (domain vision)
    (shared true)
  ))
  (children ([]
    understand_visual_world.explore_safely
    understand_visual_world.explain_dynamics
  ))
  (preferredChild understand_visual_world.explain_dynamics)
)

(
  (kind goal)
  (id understand_visual_world.explain_dynamics)
  (label "Explain Visual Dynamics")
  (description "Prefer observations and actions that produce a compact, evidence-backed model of change.")
  (priority 100)
  (evaluation (
    (primaryMetric explained_transition_coverage)
    (riskTolerance medium)
  ))
  (parents ([]
    understand_visual_world
  ))
)

(
  (kind goal)
  (id understand_visual_world.explore_safely)
  (label "Explore Safely")
  (description "Prioritize information gain while avoiding irreversible low-confidence actions.")
  (priority 80)
  (evaluation (
    (primaryMetric information_gain)
    (riskTolerance low)
  ))
  (parents ([]
    understand_visual_world
  ))
)
