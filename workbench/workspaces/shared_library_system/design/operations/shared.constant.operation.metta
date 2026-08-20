(
  (id shared.constant)
  (label "Constant Value")
  (description "Produce a configured constant value.")
  (topics ([]
    core-primitives
    sample-demos
  ))
  (inputs ())
  (outputs (
    (value Any)
  ))
  (parameters (
    (value null)
  ))
  (example_execute (
    (action operation.invoke)
    (parameters (
      (value (
        (datatype Any)
        (label "Constant value")
        (default 42)
      ))
    ))
  ))
  (children ([]
    shared.constant.workbench
  ))
  (preferredChild shared.constant.workbench)
  (kind operation)
)
