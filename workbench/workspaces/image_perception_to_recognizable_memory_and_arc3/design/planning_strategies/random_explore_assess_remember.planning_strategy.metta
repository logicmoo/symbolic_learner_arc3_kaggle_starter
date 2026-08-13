(
  (kind planning_strategy)
  (id arc3_random_player.random_explore_assess_remember)
  (label "Random Explore, Assess, and Remember")
  (description "Use bounded learned-weighted exploration now, while keeping vision and model-driven alternatives replaceable at the Operation boundary.")
  (goals ([]
    arc3_random_player.learn_by_playing
  ))
  (workflow arc3_random_player.outer_loop)
  (parameters (
    (secondsPerGame 600)
    (selectionPolicy avoid-immediate-repeat)
    (actionPolicy learned-weighted-random)
  ))
)
