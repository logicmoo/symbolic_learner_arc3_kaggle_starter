(
  (kind operation_implementation)
  (id shared.constant.workbench)
  (label "Constant Value / Workbench")
  (description "Return a value configured on the workflow step.")
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
