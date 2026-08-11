(
  (kind goal)
  (id arc3_random_player.learn_by_playing)
  (label "Learn ARC3 by Playing")
  (description "Accumulate evidence about game dynamics by repeatedly observing, acting, evaluating outcomes, and retaining reusable action knowledge.")
  (successCriteria ([]
    "Query the real ARC game catalog before choosing a game"
    "Persist every action with before/after image evidence and an outcome assessment"
    "Carry action-outcome memory into later attempts"
    "Rotate games after the configured time budget"
  ))
  (metadata (
    (domain arc3)
    (architecture outer-learning-loop)
    (visionPhase deferred-operation-alternatives)
  ))
)
