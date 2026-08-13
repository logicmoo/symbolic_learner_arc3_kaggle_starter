(
  (kind operation)
  (id shared.constant.workbench)
  (label "Constant Value / Workbench")
  (description "Return a value configured on the workflow step.")
  (categories ([] core/values sample/core))
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
