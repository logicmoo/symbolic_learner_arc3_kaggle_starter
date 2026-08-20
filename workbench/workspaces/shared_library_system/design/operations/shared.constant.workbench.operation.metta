(
  (kind operation)
  (id shared.constant.workbench)
  (label "Constant Value / Workbench")
  (description "Return a value configured on the workflow step.")
  (topics ([]
    core
    sample
  ))
  (parents ([]
    shared.constant
  ))
  (implementation system.workbench)
  (parameters (
    (capability value.constant)
    (outputBinding value)
  ))
  (outputs (
    (value Any)
  ))
)
