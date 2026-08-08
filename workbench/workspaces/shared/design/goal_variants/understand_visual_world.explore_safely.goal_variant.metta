({}
  (kind goal_variant)
  (id understand_visual_world.explore_safely)
  (label "Explore Safely")
  (description "Prioritize information gain while avoiding irreversible low-confidence actions.")
  (priority 80)
  (evaluation ({}
    (primaryMetric information_gain)
    (riskTolerance low)
  ))
  (parents (
    understand_visual_world
  ))
)
