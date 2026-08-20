(
  (id shared.select_field)
  (label "Select Record Field")
  (description "Select one field from an object artifact using the configured key.")
  (topics ([]
    core-primitives
    data-merge-select
  ))
  (implementation core.select)
  (inputs (
    (value Object)
  ))
  (outputs (
    (value Any)
  ))
  (parameters (
    (key field_name)
  ))
  (kind operation)
)
