(
  (kind operation) (id arc3_random.discover_games) (label "Discover ARC Games") (topics ([]
   arc3
 ))
  (description "Ask the real ARC service for its current game catalog.")
  (role abstract_stage) (inputs ()) (outputs ((games Array)))
  (children ([] arc3_random.discover_games.python))
  (preferredChild arc3_random.discover_games.python)
)
(
  (kind operation) (id arc3_random.discover_games.python) (label "Discover ARC Games / Python") (topics ([]
   arc3
 ))
  (description "Call Arcade.get_environments and normalize the returned records.")
  (implementation python.callable) (inputs ()) (outputs ((games Array)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable discover_games)))
  (parameters ((outputBinding games))) (parents ([] arc3_random.discover_games))
)
(
  (kind operation) (id arc3_random.curate_viewable_gallery) (label "Curate Viewable Gallery") (topics ([]
   arc3
   inspection
 ))
  (description "Curate either the available-game previews or the selected game's first screenshot as a viewable Gallery Resource.")
  (role abstract_stage) (inputs ((games Array) (workspace_root Text) (game Any) (session Object)))
  (outputs ((gallery Object)))
  (children ([] arc3_random.curate_viewable_gallery.python))
  (preferredChild arc3_random.curate_viewable_gallery.python)
)
(
  (kind operation) (id arc3_random.curate_viewable_gallery.python) (label "Curate Viewable Gallery / Python") (topics ([]
   arc3
   inspection
   sample
 ))
  (implementation python.callable) (inputs ((games Array) (workspace_root Text) (game Any) (session Object)))
  (outputs ((gallery Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable curate_viewable_gallery)))
  (parameters ((outputBinding gallery))) (parents ([] arc3_random.curate_viewable_gallery))
)
(
  (kind operation) (id arc3_random.initialize_played_games) (label "Start Empty Played-Games List") (topics ([]
   arc3
 ))
  (description "Start this workflow run with an empty ordered list of played ARC game IDs.")
  (implementation python.callable) (inputs ()) (outputs ((played_games Array)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable initialize_played_games)))
  (parameters ((outputBinding played_games)))
)
(
  (kind operation) (id arc3_random.filter_unplayed_games) (label "Filter Already-Played Games") (topics ([]
   arc3
 ))
  (description "Remove games already selected in this run; begin a new cycle only after the catalog is exhausted.")
  (implementation python.callable) (inputs ((games Array) (played_games Array))) (outputs ((games Array)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable filter_unplayed_games)))
  (parameters ((outputBinding games)))
)
(
  (kind operation) (id arc3_random.remember_played_game) (label "Remember Selected Game") (topics ([]
   arc3
 ))
  (description "Append the selected game ID to the ordered played-games list without duplicates.")
  (implementation python.callable) (inputs ((played_games Array) (game Any))) (outputs ((played_games Array)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable remember_played_game)))
  (parameters ((outputBinding played_games)))
)
(
  (kind operation) (id arc3_random.select_game) (label "Select ARC Game") (topics ([]
   arc3
 ))
  (description "Choose from a catalog already filtered to unplayed games while avoiding an immediate repeat.")
  (role abstract_stage) (inputs ((games Array) (previous_game_id Text) (seed Number)))
  (outputs ((game Object)))
  (children ([] arc3_random.select_game.random arc3_random.select_game.manual))
  (preferredChild arc3_random.select_game.random)
)
(
  (kind operation) (id arc3_random.select_game.random) (label "Select ARC Game / Select Random") (topics ([]
   arc3
 ))
  (description "Select from the live games by delegating to the reusable Random List Element behavior.")
  (implementation python.callable) (inputs ((games Array) (previous_game_id Text) (seed Number)))
  (outputs ((game Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable select_random_game)))
  (delegatesTo collection.random_list_element)
  (parameters ((outputBinding game))) (parents ([] arc3_random.select_game))
)
(
  (kind operation) (id arc3_random.select_game.manual) (label "Select ARC Game / Enter Game Name") (topics ([]
   arc3
   games
 ))
  (description "Pause so the user can type a live ARC game name or ID.")
  (implementation human.await_input) (inputs ((games Array)))
  (outputs ((game Object)))
  (parameters ((form ((game ((type Text) (prompt "Enter the ARC game name or ID")))))))
  (parents ([] arc3_random.select_game))
)
(
  (kind operation) (id arc3_random.load_game_metta_data) (label "Load Game MeTTa Data") (topics ([]
   arc3
 ))
  (description "Load the selected game's MeTTa knowledge and AtomSpace, start its live session, and capture its first visual screenshot.")
  (role abstract_stage) (inputs ((game Any) (workspace_root Text)))
  (outputs ((session Object) (controls Array) (initial_screenshot Image)))
  (children ([] arc3_random.load_game_metta_data.python))
  (preferredChild arc3_random.load_game_metta_data.python)
)
(
  (kind operation) (id arc3_random.load_game_metta_data.python) (label "Load Game MeTTa Data / Python") (topics ([]
   arc3
   sample
 ))
  (implementation python.callable) (inputs ((game Any) (workspace_root Text)))
  (outputs ((session Object) (controls Array) (initial_screenshot Image)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable load_game_metta_data)))
  (parents ([] arc3_random.load_game_metta_data))
)
(
  (kind operation) (id arc3_random.initialize_selected_game) (label "Initialize Selected ARC Game") (topics ([]
   arc3
 ))
  (description "Initialize the ARC episode through the environment API and expose its first playable frame without making a move.")
  (role abstract_stage) (inputs ((session Object)))
  (outputs ((session Object) (result Object) (initial_screenshot Image)))
  (children ([] arc3_random.initialize_selected_game.python))
  (preferredChild arc3_random.initialize_selected_game.python)
)
(
  (kind operation) (id arc3_random.initialize_selected_game.python) (label "Initialize Selected ARC Game / Python") (topics ([]
   arc3
   sample
 ))
  (implementation python.callable) (inputs ((session Object)))
  (outputs ((session Object) (result Object) (initial_screenshot Image)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable initialize_selected_game)))
  (parents ([] arc3_random.initialize_selected_game))
)
(
  (kind operation) (id arc3_random.reset_selected_game) (label "Reset Current ARC Game Level") (topics ([]
   arc3
 ))
  (description "Restore the current ARC level to its last saved checkpoint, or restart the entire selected game from level one.")
  (role abstract_stage) (inputs ((session Object) (target Text)))
  (outputs ((session Object) (result Object) (reset_screenshot Image)))
  (children ([] arc3_random.reset_selected_game.python))
  (preferredChild arc3_random.reset_selected_game.python)
)
(
  (kind operation) (id arc3_random.reset_selected_game.python) (label "Reset Current ARC Game Level / Python") (topics ([]
   arc3
   sample
 ))
  (implementation python.callable) (inputs ((session Object) (target Text)))
  (outputs ((session Object) (result Object) (reset_screenshot Image)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable reset_selected_game)))
  (example_execute ((arguments ((target ((datatype Text) (default "level") (options ([] "level" "checkpoint" "game"))))))))
  (parents ([] arc3_random.reset_selected_game))
)
(
  (kind operation) (id arc3_random.pick_random_move_and_execute) (label "Pick Random Move and Execute It") (topics ([]
   arc3
 ))
  (description "Capture the current frame, choose one legal random move, execute it, and return the resulting screenshot.")
  (role abstract_stage) (inputs ((session Object) (controls Array) (game Any) (memory Object) (seed Number) (move_limit Number)))
  (outputs ((session Object) (before Object) (proposal Object) (result Object) (next_screenshot Image) (replay_gallery Object) (animated_replay Image)))
  (children ([] arc3_random.pick_random_move_and_execute.python))
  (preferredChild arc3_random.pick_random_move_and_execute.python)
)
(
  (kind operation) (id arc3_random.pick_random_move_and_execute.python) (label "Pick Random Move and Execute It / Python") (topics ([]
   arc3
 ))
  (description "Use the live ARC session and its declared controls to advance exactly one step.")
  (implementation python.callable) (inputs ((session Object) (controls Array) (game Any) (memory Object) (seed Number) (move_limit Number)))
  (outputs ((session Object) (before Object) (proposal Object) (result Object) (next_screenshot Image) (replay_gallery Object) (animated_replay Image)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable pick_random_move_and_execute)))
  (example_execute ((arguments ((move_limit ((datatype Number) (default 10)))))))
  (parents ([] arc3_random.pick_random_move_and_execute))
)
(
  (kind operation) (id arc3_random.capture_observation) (label "Capture ARC Observation") (topics ([]
   arc3
 ))
  (description "Represent the selected game, captured frame path, state, level, and content hash as durable evidence.")
  (role abstract_stage) (inputs ((game Any) (frame_path Text) (state Text) (level Number)))
  (outputs ((observation Object)))
  (children ([] arc3_random.capture_observation.python))
  (preferredChild arc3_random.capture_observation.python)
)
(
  (kind operation) (id arc3_random.capture_observation.python) (label "Capture ARC Observation / Python") (topics ([]
   arc3
 ))
  (description "Hash the real captured image and retain its selected-game and state metadata.")
  (implementation python.callable) (inputs ((game Any) (frame_path Text) (state Text) (level Number)))
  (outputs ((observation Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable capture_observation)))
  (parameters ((outputBinding observation))) (parents ([] arc3_random.capture_observation))
)
(
  (kind operation) (id arc3_random.propose_action) (label "Propose ARC Action") (topics ([]
   arc3
 ))
  (description "Choose one legal ARC action using observation evidence and retained outcomes.")
  (role abstract_stage)
  (inputs ((action_table Array) (memory Object) (game_id Text) (state Text) (seed Number) (current_image Image)))
  (outputs ((proposal Object)))
  (children ([] arc3_random.propose_action.python arc3_random.propose_action.llm))
  (preferredChild arc3_random.propose_action.python)
)
(
  (kind operation) (id arc3_random.propose_action.python) (label "Propose ARC Action / Python") (topics ([]
   arc3
 ))
  (description "Use learned-weighted randomness, including reset and complex coordinate handling.")
  (implementation python.callable)
  (inputs ((action_table Array) (memory Object) (game_id Text) (state Text) (seed Number) (current_image Image)))
  (outputs ((proposal Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable choose_action)))
  (parameters ((outputBinding proposal))) (parents ([] arc3_random.propose_action))
)
(
  (kind operation) (id arc3_random.propose_action.llm) (label "Propose ARC Action / Prompt + Vision") (topics ([]
   arc3
 ))
  (description "Use a configured vision-capable model to propose a legal action from the same contract.")
  (implementation llm.complete)
  (inputs ((action_table Array) (memory Object) (game_id Text) (state Text) (seed Number) (current_image Image)))
  (outputs ((proposal Object)))
  (bindings ((prompts ([] structured_json_response arc3_random.propose_action)) (separator "\n\n")))
  (modelSelection ((models ([] openrouter/free)) (strategy single)))
  (parameters ((inputBinding action_table) (outputBinding proposal))) (parents ([] arc3_random.propose_action))
)
(
  (kind operation) (id arc3_random.assess_transition) (label "Assess ARC Transition") (topics ([]
   arc3
 ))
  (description "Explain what an action did well or poorly from before/after evidence.")
  (role abstract_stage) (inputs ((before Object) (after Object))) (outputs ((assessment Object)))
  (children ([] arc3_random.assess_transition.python arc3_random.assess_transition.llm))
  (preferredChild arc3_random.assess_transition.python)
)
(
  (kind operation) (id arc3_random.execute_action) (label "Execute ARC Action") (topics ([]
   arc3
 ))
  (description "Apply exactly one proposed legal action through the bound ARC runner and return its resulting observable state.")
  (role abstract_stage) (inputs ((session Object) (proposal Object)))
  (outputs ((result Object)))
  (children ([] arc3_random.execute_action.python))
  (preferredChild arc3_random.execute_action.python)
)
(
  (kind operation) (id arc3_random.execute_action.python) (label "Execute ARC Action / Python") (topics ([]
   arc3
 ))
  (description "Call the live runner for one action without owning the surrounding learning tree.")
  (implementation python.callable) (inputs ((session Object) (proposal Object)))
  (outputs ((result Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable execute_action)))
  (parameters ((outputBinding result))) (parents ([] arc3_random.execute_action))
)
(
  (kind operation) (id arc3_random.assess_transition.python) (label "Assess ARC Transition / Python") (topics ([]
   arc3
 ))
  (description "Apply deterministic win, loss, level, and frame-change rules.")
  (implementation python.callable) (inputs ((before Object) (after Object))) (outputs ((assessment Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable assess_transition)))
  (parameters ((outputBinding assessment))) (parents ([] arc3_random.assess_transition))
)
(
  (kind operation) (id arc3_random.assess_transition.llm) (label "Assess ARC Transition / Prompt + Vision") (topics ([]
   arc3
 ))
  (description "Use a configured model to produce a richer evidence-backed critique.")
  (implementation llm.complete) (inputs ((before Object) (after Object))) (outputs ((assessment Object)))
  (bindings ((prompts ([] structured_json_response arc3_random.critique_transition)) (separator "\n\n")))
  (modelSelection ((models ([] openrouter/free)) (strategy single)))
  (parameters ((inputBinding before) (outputBinding assessment))) (parents ([] arc3_random.assess_transition))
)
(
  (kind operation) (id arc3_random.update_memory) (label "Update ARC Learning Memory") (topics ([]
   arc3
 ))
  (description "Accumulate good, bad, and neutral action evidence for later sessions.")
  (role abstract_stage) (inputs ((memory Object) (game_id Text) (action Text) (assessment Object)))
  (outputs ((memory Object)))
  (children ([] arc3_random.update_memory.python))
  (preferredChild arc3_random.update_memory.python)
)
(
  (kind operation) (id arc3_random.update_memory.python) (label "Update ARC Learning Memory / Python") (topics ([]
   arc3
 ))
  (description "Update immutable JSON-compatible per-game action statistics.")
  (implementation python.callable) (inputs ((memory Object) (game_id Text) (action Text) (assessment Object)))
  (outputs ((memory Object)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable update_learning_memory)))
  (parameters ((outputBinding memory))) (parents ([] arc3_random.update_memory))
)
(
  (kind operation) (id arc3_random.seen_enough) (label "Have You Seen Enough?") (topics ([]
   arc3
   games
 ))
  (description "After each displayed move, let the user continue watching or finish the current game loop.")
  (role abstract_stage) (inputs ()) (outputs ((rotate Boolean)))
  (children ([] arc3_random.seen_enough.human))
  (preferredChild arc3_random.seen_enough.human)
)
(
  (kind operation) (id arc3_random.seen_enough.human) (label "Have You Seen Enough? / Ask User") (topics ([]
   arc3
   games
 ))
  (implementation human.await_input) (inputs ()) (outputs ((rotate Boolean)))
  (parameters ((form ((rotate ((type Boolean) (prompt "Have you seen enough of this game? Continue when false; finish when true.")))))))
  (parents ([] arc3_random.seen_enough))
)
(
  (kind operation) (id arc3_random.should_rotate) (label "Test Game Time Budget") (topics ([]
   arc3
 ))
  (description "Decide whether the current game has exhausted its configured play budget.")
  (role abstract_stage) (inputs ((started_monotonic Number) (duration_seconds Number) (now_monotonic Number)))
  (outputs ((rotate Boolean)))
  (children ([] arc3_random.should_rotate.python))
  (preferredChild arc3_random.should_rotate.python)
)
(
  (kind operation) (id arc3_random.should_rotate.python) (label "Test Game Time Budget / Python") (topics ([]
   arc3
 ))
  (description "Compare monotonic timestamps without coupling the loop to wall-clock time.")
  (implementation python.callable) (inputs ((started_monotonic Number) (duration_seconds Number) (now_monotonic Number)))
  (outputs ((rotate Boolean)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable should_rotate)))
  (parameters ((outputBinding rotate))) (parents ([] arc3_random.should_rotate))
)
(
  (kind operation) (id arc3_random.run_session) (label "Run ARC Random-Learning Session") (topics ([]
   arc3
 ))
  (description "Execute the real outer loop and persist runtime evidence for one or more games.")
  (role abstract_stage)
  (inputs ((workspace_root Text) (seconds_per_game Number) (max_games Number) (move_limit Number) (seed Number) (mode Text)))
  (outputs ((sessions Array)))
  (children ([] arc3_random.run_session.python))
  (preferredChild arc3_random.run_session.python)
)
(
  (kind operation) (id arc3_random.run_session.python) (label "Run ARC Random-Learning Session / Python") (topics ([]
   arc3
 ))
  (description "Invoke the live ARC runner using the same decomposed operation contracts.")
  (implementation python.callable)
  (inputs ((workspace_root Text) (seconds_per_game Number) (max_games Number) (move_limit Number) (seed Number) (mode Text)))
  (outputs ((sessions Array)))
  (python ((importMode file) (file python/arc3_random_player.py) (callable run_random_arc3_session)))
  (example_execute ((arguments ((seconds_per_game ((datatype Number) (default 60))) (max_games ((datatype Number) (default null))) (move_limit ((datatype Number) (default 10))) (seed ((datatype Number) (default 0))) (mode ((datatype Text) (default "automatic") (options ([] "interactive" "automatic"))))))))
  (parameters ((outputBinding sessions))) (parents ([] arc3_random.run_session))
)
