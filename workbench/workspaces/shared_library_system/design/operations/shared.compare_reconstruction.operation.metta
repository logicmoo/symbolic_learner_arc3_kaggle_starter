(
  (id shared.compare_reconstruction)
  (label "Compare Reconstruction")
  (description "Compare a source observation with a reconstructed observation and emit evidence. Generic validation operation.")
  (topics ([]
    vision
    graphics
    world-modeling
  ))
  (implementation vision.diff)
  (inputs (
    (source Observation)
    (reconstruction Observation)
  ))
  (outputs (
    (evidence EvidenceBundle)
  ))
  (parameters ())
  (kind operation)
)
