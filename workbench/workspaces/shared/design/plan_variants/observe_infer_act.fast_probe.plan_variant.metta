({}
  (kind plan_variant)
  (id observe_infer_act.fast_probe)
  (label "Fast Probe")
  (description "Use short exploratory sequences to identify mechanics quickly.")
  (workflow vision_learn_by_observation)
  (strategy ({}
    (maxUnverifiedActions 3)
    (requireExplanation false)
    (replanOnContradiction true)
  ))
  (parents (
    observe_infer_act
  ))
)
