(
  (kind plan_variant)
  (id observe_infer_act.conservative_loop)
  (label "Conservative Learning Loop")
  (description "Require transition evidence before escalating to higher-risk actions.")
  (workflow vision_observe_choose_record)
  (strategy (
    (maxUnverifiedActions 1)
    (requireExplanation true)
    (replanOnContradiction true)
  ))
  (parents ([]
    observe_infer_act
  ))
)
