(
  (kind workflow)
  (id arc3_random_player.outer_loop)
  (label "ARC3 Random Player Outer Loop")
  (description "A reusable learning-tree topology that plays and displays one move at a time, repeating until the user says they have seen enough.")
  (inputs (
    (mode Text)
    (move_limit Number)
    (workspace_root Text)
    (previous_game_id Text)
    (memory Object)
    (seconds_per_game Number)
    (seed Number)
  ))
  (inputDefaults (
    (mode automatic)
    (move_limit 10)
    (workspace_root "")
    (previous_game_id "")
    (memory ())
    (seconds_per_game 60)
    (seed 0)
  ))
  (outputs (
    (game $game)
    (next_game $next_game)
    (played_games $played_games_after_next_selection)
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
      (id initialize_played_games)
      (label "Start Empty Played-Games List")
      (kind operation)
      (operation echo.value)
      (inputs (
        (played_games ([]))
      ))
      (outputs ([]
        played_games
      ))
    )
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
      (id filter_unplayed_games)
      (label "Filter Already-Played Games")
      (kind operation)
      (operation arc3_random.filter_unplayed_games)
      (dependsOn ([]
        discover_games
        initialize_played_games
      ))
      (inputs (
        (games $games)
        (played_games $played_games)
      ))
      (outputs (
        (games unplayed_games)
      ))
    )
    (
      (id curate_viewable_gallery)
      (label "Curate Viewable Gallery")
      (kind operation)
      (operation arc3_random.curate_viewable_gallery)
      (probe (
        (enabled false)
        (required false)
        (blocking false)
      ))
      (dependsOn ([]
        filter_unplayed_games
      ))
      (inputs (
        (games $unplayed_games)
        (workspace_root $workspace_root)
      ))
      (outputs (
        (gallery game_preview_gallery)
      ))
    )
    (
      (id select_game)
      (label "Select a game")
      (kind operation)
      (operation arc3_random.select_game)
      (dependsOn ([]
        filter_unplayed_games
      ))
      (inputs (
        (games $unplayed_games)
        (previous_game_id $previous_game_id)
        (seed $seed)
        (move_limit $move_limit)
      ))
      (outputs (
        (game game)
      ))
    )
    (
      (id remember_selected_game)
      (label "Remember Selected Game")
      (kind operation)
      (operation arc3_random.remember_played_game)
      (dependsOn ([]
        select_game
        initialize_played_games
      ))
      (inputs (
        (played_games $played_games)
        (game $game)
      ))
      (outputs (
        (played_games played_games_after_selection)
      ))
    )
    (
      (id load_game_metta_data)
      (label "Load Game MeTTa Data")
      (kind operation)
      (operation arc3_random.load_game_metta_data)
      (dependsOn ([]
        select_game
      ))
      (inputs (
        (game $game)
        (workspace_root $workspace_root)
      ))
      (outputs (
        (session game_session)
        (controls action_table)
        (initial_screenshot initial_screenshot)
      ))
    )
    (
      (id curate_selected_game_gallery)
      (label "Curate Viewable Gallery")
      (kind operation)
      (operation arc3_random.curate_viewable_gallery)
      (probe (
        (enabled false)
        (required false)
        (blocking false)
      ))
      (dependsOn ([]
        load_game_metta_data
      ))
      (inputs (
        (game $game)
        (session $game_session)
      ))
      (outputs (
        (gallery selected_game_gallery)
      ))
    )
    (
      (id initialize_selected_game)
      (label "Initialize Selected ARC Game")
      (kind operation)
      (operation arc3_random.initialize_selected_game)
      (dependsOn ([]
        load_game_metta_data
      ))
      (inputs (
        (session $game_session)
      ))
      (outputs (
        (session initialized_game_session)
        (result initialization_result)
        (initial_screenshot initial_game_screenshot)
      ))
    )
    (
      (id pick_random_move_and_execute)
      (label "Pick Random Move and Execute It")
      (kind operation)
      (operation arc3_random.pick_random_move_and_execute)
      (dependsOn ([]
        initialize_selected_game
      ))
      (inputs (
        (session $initialized_game_session)
        (controls $action_table)
        (game $game)
        (memory $memory)
        (seed $seed)
        (move_limit $move_limit)
      ))
      (outputs (
        (session moved_game_session)
        (before before)
        (proposal proposal)
        (result action_result)
        (next_screenshot next_screenshot)
        (replay_gallery replay_gallery)
        (animated_replay animated_replay)
      ))
    )
    (
      (id capture_after)
      (label "Capture the resulting image")
      (kind operation)
      (operation arc3_random.capture_observation)
      (dependsOn ([]
        pick_random_move_and_execute
      ))
      (inputs (
        (game $game)
        (frame_path $next_screenshot)
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
        pick_random_move_and_execute
        capture_after
      ))
      (while (
        (condition $assessment.frame_changed)
        (operator equals)
        (conditionPort false)
        (maxIterations 32)
        (targetStepId pick_random_move_and_execute)
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
      (id ask_if_seen_enough)
      (label "Have You Seen Enough?")
      (kind operation)
      (operation arc3_random.seen_enough)
      (dependsOn ([]
        remember_outcome
      ))
      (inputs ())
      (outputs (
        (rotate rotate)
      ))
    )
    (
      (id filter_games_for_next_selection)
      (label "Filter Games for Next Selection")
      (kind operation)
      (operation arc3_random.filter_unplayed_games)
      (dependsOn ([]
        ask_if_seen_enough
        discover_games
        remember_selected_game
      ))
      (inputs (
        (games $games)
        (played_games $played_games_after_selection)
      ))
      (outputs (
        (games games_for_next_selection)
      ))
    )
    (
      (id select_next_game)
      (label "Select Another Unplayed Game")
      (kind operation)
      (operation arc3_random.select_game)
      (implementationVariant arc3_random.select_game.random)
      (dependsOn ([]
        filter_games_for_next_selection
      ))
      (inputs (
        (games $games_for_next_selection)
        (previous_game_id $game.game_id)
        (seed $seed)
      ))
      (outputs (
        (game next_game)
      ))
    )
    (
      (id remember_next_game)
      (label "Remember Next Selected Game")
      (kind operation)
      (operation arc3_random.remember_played_game)
      (dependsOn ([]
        select_next_game
        remember_selected_game
      ))
      (inputs (
        (played_games $played_games_after_selection)
        (game $next_game)
      ))
      (outputs (
        (played_games played_games_after_next_selection)
      ))
    )
    (
      (id play_all_remaining_games_automatically)
      (label "While Unplayed Games Remain, Play Next Game")
      (kind operation)
      (operation arc3_random.run_session)
      (dependsOn ([]
        filter_unplayed_games
      ))
      (while ([]
        (
          (condition $unplayed_games)
          (operator not_empty)
          (maxIterations 100)
        )
        (
          (condition $elapsed_game_seconds)
          (operator less_than)
          (conditionPort $seconds_per_game)
          (maxIterations 1000)
        )
      ))
      (inputs (
        (workspace_root $workspace_root)
        (seconds_per_game $seconds_per_game)
        (max_games null)
        (move_limit $move_limit)
        (seed $seed)
        (mode $mode)
      ))
      (outputs (
        (sessions automatic_sessions)
      ))
    )
  ))
  (workspaceId arc3_random_player)
)
