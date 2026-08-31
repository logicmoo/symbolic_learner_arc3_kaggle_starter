(
  (kind planning_strategy)
  (id observe_infer_act)
  (label "Observe, Infer, Act")
  (description "Convert observations into symbolic hypotheses, choose an action, and construct an executable Workflow/plan.")
  (goals ([]
    understand_visual_world
  ))
  (implementedBy (
    (observe_infer_act.conservative_loop ())
    (observe_infer_act.fast_probe ())
  ))
  (inheritedBy (
    (observe_infer_act.conservative_loop (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (observe_infer_act.fast_probe (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (preferredImplementation observe_infer_act.conservative_loop)
)
(
  (kind planning_strategy)
  (id observe_infer_act.conservative_loop)
  (label "Observe, Infer, Act / Conservative Loop")
  (description "Prefer verified observations and bounded iteration before committing an action.")
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
(
  (kind planning_strategy)
  (id observe_infer_act.fast_probe)
  (label "Observe, Infer, Act / Fast Probe")
  (description "Prefer a small informative action early, then revise the Workflow from the resulting evidence.")
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
