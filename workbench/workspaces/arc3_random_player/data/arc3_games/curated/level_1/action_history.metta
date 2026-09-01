([]
  (
    (step 0)
    (command ROOT)
    (expected_effect "establish baseline objects from first image and plan trigger route")
    (actual_effect "baseline catalog fixed from first image; no transition applied")
    (surprises ([]
      none
    ))
    (unexpected_effects ([]
      none
    ))
    (predicted_destination "toward plus_sign trigger")
    (predicted_next_state "next move should position player for trigger contact")
    (scene_ascii_lines ([]
      "+----------------+"
      "| @  +  O   ##   |"
      "| ..PLAYFIELD..  |"
      "+----------------+"
    ))
    (change_ascii_lines ([]
      "STEP 0 CMD ROOT"
      "before:  +  O>"
      "after :  +  O>"
      "delta :  baseline only"
    ))
  )
)
