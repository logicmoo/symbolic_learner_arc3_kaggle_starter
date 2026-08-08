({}
  (kind plan)
  (id observe_infer_act)
  (label "Observe, Infer, Act")
  (description "Convert observations into symbolic hypotheses, choose an action, and record the transition.")
  (goals (
    understand_visual_world
  ))
  (children (
    observe_infer_act.conservative_loop
    observe_infer_act.fast_probe
  ))
  (preferredChild observe_infer_act.conservative_loop)
)
