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
  (kind operation)
  (implementedBy (
    (shared.constant.workbench ())
  ))
  (inheritedBy (
    (shared.constant.workbench (
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
  (preferredImplementation shared.constant.workbench)
)
