(
  (kind operation)
  (id sample.request_number.workbench)
  (label "Request a Number / Workbench")
  (description "Materialize the request as a durable human-input workflow step.")
  (categories ([] sample/user_input system/workbench))
  (parents ([]
    sample.request_number
  ))
  (implementation system.workbench)
  (parameters (
    (capability input.request)
    (outputBinding value)
  ))
  (outputs (
    (value Number)
  ))
)
