(
  (id echo.value)
  (label "Echo Named Value")
  (description "Publish the supplied played-games list unchanged under the same output name.")
  (topics ([]
    core
    arc3
  ))
  (implementation echo.value)
  (inputs (
    (played_games Array)
  ))
  (outputs (
    (played_games Array)
  ))
  (parameters ())
  (kind operation)
)
