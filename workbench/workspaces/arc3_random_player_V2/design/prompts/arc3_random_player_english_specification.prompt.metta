(
  (kind prompt)
  (id arc3_random_player.english_workflow_specification)
  (label "ARC3 Random Player / English Workflow Specification")
  (description "The authoritative plain-English semantic specification used to regenerate the ARC3 Random Player workflow.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Build a bounded ARC3 learning workflow using only games and operations supplied by the runtime catalogs."
    "Start with an empty played-games list, discover the live ARC game catalog, filter out played games, build a gallery, choose an unplayed game, remember it, load its MeTTa data and controls, and initialize its session."
    "While unplayed games remain, play the next selected game. Within each game, continue while elapsed game time is below seconds_per_game, subject to the move limit. Use shared control.while operations with explicit finite bounds."
    "For each move, choose one legal action from retained learning evidence, execute it, capture the resulting observation, compare before and after evidence, and retain a good, bad, or neutral assessment."
    "When assessment.frame_changed is false, remember the action as ineffective, temporarily exclude it, and return to move selection to choose a different legal action. Bound this retry loop and clear temporary exclusions after a visible state change."
    "After a game ends, its limit is reached, or rotation is requested, filter the catalog using the updated played-games list and continue only when another unplayed game exists."
    "Return the played-games list, learning memory, observations, assessments, galleries, and automatic session summaries with provenance. Preserve stable step IDs and all reachable input/output bindings when updating an existing workflow."
    "Generate semantic operation references first. Do not prematurely choose Python, Prolog, LLM, or other concrete implementations; preflight or runtime resolves them after the complete workflow exists."
    "Preflight may infer and adjust bounded loops, reevaluation checkpoints, retained/reset iteration values, and Bicameral Mode CoT cadence from the completed dataflow."
  ))
)
