(
  (id shared.capture_observation)
  (label "Capture Observation")
  (description "Persist an observation unchanged so downstream steps can reference a stable artifact. Reusable by visual, board-game, robotics, and other worlds.")
  (topics ([]
    observation
    world-modeling
    core-primitives
  ))
  (implementation core.echo)
  (inputs (
    (value Any)
  ))
  (outputs (
    (value Any)
  ))
  (parameters ())
  (kind operation)
)
