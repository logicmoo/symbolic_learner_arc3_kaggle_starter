(
  (id shared.merge_records)
  (label "Merge Records")
  (description "Merge two object records into one derived record. Useful for combining observations, actions, metadata, evidence, and results.")
  (topics ([]
    core-primitives
    data-merge-select
  ))
  (implementation core.merge)
  (inputs (
    (left Object)
    (right Object)
  ))
  (outputs (
    (value Object)
  ))
  (parameters ())
  (kind operation)
)
