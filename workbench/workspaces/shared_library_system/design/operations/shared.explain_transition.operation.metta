(
  (id shared.explain_transition)
  (label "Explain State Transition")
  (description "Explain a before/action/after transition as hypotheses and evidence. Generic world-learning operation.")
  (topics ([]
    symbolic
    world-modeling
    learning
  ))
  (implementation symbolic.transition)
  (inputs (
    (before Observation)
    (action Intervention)
    (after Observation)
  ))
  (outputs (
    (hypotheses HypothesisSet)
  ))
  (parameters ())
  (kind operation)
)
