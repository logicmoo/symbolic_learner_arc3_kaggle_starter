(
  (kind operation_implementation)
  (id sample.request_number.workbench)
  (label "Request a Number / Workbench")
  (description "Materialize the request as a durable human-input workflow step.")
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
