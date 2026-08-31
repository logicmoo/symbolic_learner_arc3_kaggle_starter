(
  (kind operation)
  (id sample.request_number.workbench)
  (label "Request a Number / Workbench")
  (description "Materialize the request as a durable human-input workflow step.")
  (topics ([]
    sample-demos
    systems-workbench
  ))
  (implements (
    (sample.request_number ())
  ))
  (implementation system.workbench)
  (parameters (
    (capability input.request)
    (outputBinding value)
  ))
  (outputs (
    (value Number)
  ))
  (inheritsFrom (
    (sample.request_number (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
