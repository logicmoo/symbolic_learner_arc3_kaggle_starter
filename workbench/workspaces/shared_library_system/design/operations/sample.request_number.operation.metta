(
  (kind operation)
  (id sample.request_number)
  (label "Request a Number")
  (description "Pause a workflow and ask its user to enter a number in the Workbench UI.")
  (topics ([]
    sample-demos
    core-primitives
  ))
  (inputs ())
  (outputs (
    (value Number)
  ))
  (parameters (
    (prompt "How many objects are visible?")
    (label "Object count")
    (datatype Number)
    (required true)
  ))
  (example_execute (
    (action operation.invoke)
    (parameters (
      (prompt (
        (datatype Text)
        (label Question)
        (default "How many objects are visible?")
      ))
      (label (
        (datatype Text)
        (label "Field label")
        (default "Object count")
      ))
      (datatype (
        (datatype Text)
        (label "Expected datatype")
        (default Number)
      ))
      (required (
        (datatype Boolean)
        (label Required)
        (default true)
      ))
    ))
  ))
  (specializations (
    (sample.request_number.workbench (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization sample.request_number.workbench)
)
