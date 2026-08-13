(
  (kind planning_strategy)
  (id observe_infer_act)
  (label "Observe, Infer, Act")
  (description "Convert observations into symbolic hypotheses, choose an action, and construct an executable Workflow/plan.")
  (goals ([]
    understand_visual_world
  ))
  (children ([]
    observe_infer_act.conservative_loop
    observe_infer_act.fast_probe
  ))
  (preferredChild observe_infer_act.conservative_loop)
)
