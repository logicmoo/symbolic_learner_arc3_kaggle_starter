(
  (kind planning_strategy)
  (id observe_infer_act.conservative_loop)
  (label "Conservative Learning Loop")
  (description "Require transition evidence before escalating to higher-risk actions.")
  (workflow vision_observe_choose_record)
  (strategy (
    (maxUnverifiedActions 1)
    (requireExplanation true)
    (replanOnContradiction true)
  ))
  (implements (
    (observe_infer_act ())
  ))
  (inheritsFrom (
    (observe_infer_act (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
