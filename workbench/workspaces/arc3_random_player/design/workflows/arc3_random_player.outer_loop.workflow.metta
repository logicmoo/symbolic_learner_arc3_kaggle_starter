(
  (kind workflow)
  (id arc3_random_player.outer_loop)
  (label "ARC3 Random Player Outer Loop")
  (description "A reusable learning-tree topology whose ARC3-specific behavior is supplied entirely by operation bindings. A generic workflow runner executes the dependency tree and repeats it until the rotation decision is true.")
  (inputs (
    (workspace_root Text)
    (previous_game_id Text)
    (memory Object)
    (seconds_per_game Number)
    (started_monotonic Number)
    (now_monotonic Number)
    (seed Number)
    (runner Object)
    (frame_path Text)
    (state Text)
    (level Number)
    (action_table Array)
  ))
  (outputs (
    (game $game)
    (proposal $proposal)
    (assessment $assessment)
    (memory $updated_memory)
    (rotate $rotate)
  ))
  (planProvenance (
    (kind human)
    (strategy arc3_random_player.random_explore_assess_remember)
    (runner generic.workflow_tree)
  ))
  (steps ([]
    (
      (id discover_games)
      (label "Ask ARC server for games")
      (kind operation)
      (operation arc3_random.discover_games)
      (outputs (
        (games games)
      ))
    )
    (
      (id build_game_preview_gallery)
      (label "Build the Game Preview Gallery")
      (kind operation)
      (operation arc3_random.build_game_preview_gallery)
      (dependsOn ([]
        discover_games
      ))
      (inputs (
        (games $games)
        (workspace_root $workspace_root)
      ))
      (outputs (
        (gallery arc_preview_candidates)
      ))
    )
    (
      (id curate_game_preview_gallery)
      (label "Render the neutral Gallery Resource")
      (kind operation)
      (operation gallery.curate_resource)
      (dependsOn ([]
        build_game_preview_gallery
      ))
      (inputs (
        (items $arc_preview_candidates.games)
      ))
      (outputs (
        (gallery game_preview_gallery)
      ))
    )
    (
      (id select_game)
      (label "Choose a random previewed game")
      (kind operation)
      (operation collection.random_list_element)
      (dependsOn ([]
        curate_game_preview_gallery
      ))
      (inputs (
        (items $game_preview_gallery.items)
        (seed $seed)
      ))
      (outputs (
        (element game)
      ))
    )
    (
      (id capture_before)
      (label "Capture the current image")
      (kind operation)
      (operation arc3_random.capture_observation)
      (dependsOn ([]
        select_game
      ))
      (inputs (
        (frame_path $frame_path)
        (state $state)
        (level $level)
      ))
      (outputs (
        (observation before)
      ))
    )
    (
      (id propose_action)
      (label "Guess a legal move")
      (kind operation)
      (operation arc3_random.propose_action)
      (dependsOn ([]
        capture_before
      ))
      (inputs (
        (action_table $action_table)
        (memory $memory)
        (game_id $game.game_id)
        (state $before.state)
        (seed $seed)
        (current_image $before.frame_path)
      ))
      (outputs (
        (proposal proposal)
      ))
    )
    (
      (id execute_action)
      (label "Play the move")
      (kind operation)
      (operation arc3_random.execute_action)
      (dependsOn ([]
        propose_action
      ))
      (inputs (
        (runner $runner)
        (proposal $proposal)
      ))
      (outputs (
        (result action_result)
      ))
    )
    (
      (id capture_after)
      (label "Capture the resulting image")
      (kind operation)
      (operation arc3_random.capture_observation)
      (dependsOn ([]
        execute_action
      ))
      (inputs (
        (frame_path $action_result.frame_path)
        (state $action_result.state)
        (level $action_result.level)
      ))
      (outputs (
        (observation after)
      ))
    )
    (
      (id assess_transition)
      (label "Notice what was good or bad")
      (kind operation)
      (operation arc3_random.assess_transition)
      (dependsOn ([]
        capture_before
        capture_after
      ))
      (inputs (
        (before $before)
        (after $after)
      ))
      (outputs (
        (assessment assessment)
      ))
    )
    (
      (id remember_outcome)
      (label "Remember the outcome")
      (kind operation)
      (operation arc3_random.update_memory)
      (dependsOn ([]
        assess_transition
      ))
      (inputs (
        (memory $memory)
        (game_id $game.game_id)
        (action $proposal.action)
        (assessment $assessment)
      ))
      (outputs (
        (memory updated_memory)
      ))
    )
    (
      (id decide_repeat_or_rotate)
      (label "Repeat or rotate after the time budget")
      (kind operation)
      (operation arc3_random.should_rotate)
      (dependsOn ([]
        remember_outcome
      ))
      (inputs (
        (started_monotonic $started_monotonic)
        (duration_seconds $seconds_per_game)
        (now_monotonic $now_monotonic)
      ))
      (outputs (
        (rotate rotate)
      ))
    )
  ))
  (workspaceId arc3_random_player)
  (version 1)
)
