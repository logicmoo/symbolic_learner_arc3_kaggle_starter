(
  (kind goal_variant)
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
