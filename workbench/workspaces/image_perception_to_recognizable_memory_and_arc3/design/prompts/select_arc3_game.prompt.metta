(
  (kind prompt)
  (id arc3_random.select_game)
  (label "Select an ARC3 Game")
  (description "Choose one game from a live ARC catalog without inventing unavailable games.")
  (specializations (
    (arc3_random.select_game.default (
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
  (preferredSpecialization arc3_random.select_game.default)
)
(
  (kind prompt)
  (id arc3_random.select_game.default)
  (label "Select an ARC3 Game — Default")
  (version 1)
  (targets ([]
    generic-chat
  ))
  (implements (
    (arc3_random.select_game (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (text ([]
    "Choose exactly one game from the supplied live ARC catalog."
    "Avoid the previous game when another option exists."
    "Return JSON with game_id and a short selection_reason."
  ))
)
