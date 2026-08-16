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
(
  (kind planning_strategy)
  (id observe_infer_act.conservative_loop)
  (label "Observe, Infer, Act / Conservative Loop")
  (description "Prefer verified observations and bounded iteration before committing an action.")
  (parents ([]
    observe_infer_act
  ))
)
(
  (kind planning_strategy)
  (id observe_infer_act.fast_probe)
  (label "Observe, Infer, Act / Fast Probe")
  (description "Prefer a small informative action early, then revise the Workflow from the resulting evidence.")
  (parents ([]
    observe_infer_act
  ))
)
