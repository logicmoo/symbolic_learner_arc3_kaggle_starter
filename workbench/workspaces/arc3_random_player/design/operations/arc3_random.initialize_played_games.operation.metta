(
  (kind operation)
  (id arc3_random.initialize_played_games)
  (label "Start Empty Played-Games List")
  (topics ([]
    arc3
    systems-python
  ))
  (description "Start this workflow run with an empty ordered list of played ARC game IDs.")
  (implementation python.callable)
  (inputs ())
  (outputs (
    (played_games Array)
  ))
  (python (
    (importMode file)
    (file python/arc3_random_player.py)
    (callable initialize_played_games)
  ))
  (parameters (
    (outputBinding played_games)
  ))
)
