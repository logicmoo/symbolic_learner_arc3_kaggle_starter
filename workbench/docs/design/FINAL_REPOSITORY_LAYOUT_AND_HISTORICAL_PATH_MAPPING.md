[← Back to top-level README](../../../README.md)

# Final Repository Layout and Historical Path Mapping

Approved-decision record (Q1–Q12 resolved with Douglas, 2026-09-06/07).
Working reference for the historical replay. Repo tip at decision time: c2a6164e (main, 1751 commits, 26 merges).
Status: **mapping approved; replay not yet started.** No files move until the replay branch is built and reviewed.

## Decisions (Q1–Q12)
- Q1  Workbench core stack (engines, providers, resolution, libraries, resource layer):
      COPY_HISTORY into BOTH workbench_api_server/ AND python/omega_vision/services/.
- Q2  job_manager.py: COPY_HISTORY both (workbench_api_server/job_manager.py + python/omega_vision/services/jobs.py).
- Q3  arc3_play_api.py: COPY_HISTORY both (workbench_api_server/arc3_play_api.py + python/omega_vision/services/arc3_play.py).
- Q4  Shared bridges OV-owned: swipl_bridge.py, image_codec.py, gpt_bridge.py -> python/omega_vision/;
      arc_cli_debugger imports omega_vision. arc3_runner.py stays debugger-owned.
- Q5  Vision frontend pages single-home in frontend/packages/omega_vision_ui/;
      empty frontend/apps/omega_vision/ shell scaffolded AFTER replay (new commit, not historical).
- Q6  python/arc3_random_player.py -> python/arc_cli_debugger/arc3_random_player.py.
- Q7  Legacy /analyze + /runs still wanted: store.py, routes/, models.py stay first-class in workbench_api_server/.
- Q8  object_memory replays at python/omega_vision/ WITH FINAL SUBPACKAGE LAYOUT from birth
      (file map from rename detection of c509dc49 + ee8a9abb). The short-lived facade package
      (old python/omega_vision/, deleted pre-tip) is DROPPED from replay; facade-only commits are skipped.
- Q9  arc3_agent.pl + arc3_debugger.pl -> prolog/omega_vision/ (pack).
- Q10 Plugin framework -> TOP-LEVEL plugins_framework_src/ (plugin_admin.py SDK + plugin_api.py).
- Q11 knowledge/object_memory.db.pl (untracked, generated) -> data/omega_vision/knowledge/ (no history).
- Q12 Debugger tests -> NEW tests/arc_cli_debugger/.

## COPY_HISTORY set (each file committed at BOTH destinations through all of replay)
From workbench/server/ -> workbench_api_server/<name>.py AND python/omega_vision/services/<name>.py:
  workflow_engine.py, advanced_workflow_engine.py, workflow_providers.py, operation_resolution.py,
  operation_library.py, prompt_library.py, model_library.py, backend_library.py,
  datatype_library.py, policy_library.py, goal_plan_library.py, artifact_category_library.py,
  workspace_inheritance.py, workspace_config.py, workspace_credentials.py, model_selection_settings.py,
  resource_store.py, resource_relationships.py, resource_convention.py, metta_resource_codec.py,
  job_manager.py (services side named jobs.py), arc3_play_api.py (services side named arc3_play.py)
Rules: every historical change to the source path applies to both descendants; divergence begins only in
post-replay refactor commits; record divergence point in the commit map.

## MOVE mapping (single-destination), applied to every historical commit
### workbench/server/ -> workbench_api_server/
  app.py, terminal_api.py, mailbox_api_lib.py, jobs_api.py, datatype_api.py, prompt_api.py,
  goal_run_api.py, operation_api.py, policy_api.py, system_control_api.py, service_monitor_api.py,
  repository_docs_api.py, workflow_engine_api.py, workspace_api.py, model_policy_todo_api.py,
  workflow_runner_todo_api.py, model_discovery.py, model_policy_ping.py, model_benchmark.py,
  representation_planner.py, pddl_plan.py, store.py, models.py, routes/**, requirements.txt,
  test_*.py (5 embedded server tests -> tests/workbench_api/ instead, see Tests)
### workbench/server/ -> plugins_framework_src/
  plugin_admin.py, plugin_api.py
### workbench/server/ -> python/omega_vision/services/
  video_import_pipeline.py, video_import_api.py, registry_api.py, phase3_pipeline.py (as phase3_live.py)
### workbench/server/ -> python/omega_vision/
  generative_vision/prolog/{symbolic_arc,pixels_to_grid,pixels_to_regions,scene_split,color_names}.py
    -> python/omega_vision/perception/
  generative_vision/__init__.py, generative_vision/prolog/__init__.py -> python/omega_vision/perception/ (merged inits)
  recognition_demos.py -> python/omega_vision/demos/recognition_demos.py
  runtime.py -> python/omega_vision/perception/grid_analysis.py
### workbench/server/ -> prolog/omega_vision/
  generative_vision/prolog/{arc_parts,arc_group,group_regions,object_memory}.pl
### workbench/server/ -> workspaces/
  shared_operation_callables.py -> workspaces/titlecase_demo/ (exact spot decided at replay)
### prolog/
  KEEP prolog/: (none stay at root except future pack.pl)
  -> prolog/omega_vision/: object_memory_contract.pl, generative_form.pl, residual_gate.pl,
     single_writer.pl, transition_analysis.pl, transformation_learning.pl, rule_induction.pl,
     rule_ranking.pl, transition_rules.pl, prediction_ledger.pl, prediction_evaluation.pl,
     game_object_learner_api.pl, turtle_dsl.pl, world_state.pl (unresolved status noted),
     arc3_agent.pl, arc3_debugger.pl, demo_operation.pl (examples/ subdir ok)
  -> tests/plt/: run_tests.pl, test_object_memory.pl, test_turtle_dsl.pl, test_wide_pen_visual.pl
### python/ (ARC CLI debugger consolidation)
  interactive_runner.py, arc3_runner.py, action_tree.py, ansi_console.py, arc_interactive_sync.py,
  arc3_random_player.py -> python/arc_cli_debugger/
  webui/** + scripts/run_webui.py(+.bat) -> python/arc_cli_debugger/webui/
  scripts/{interactive_runner(.py/.bat), prolog_controlled_runner, re_play, my_play, me_play, he_play,
  play_local, play_random_arc3, windows_action_tree_smoke}.py -> python/arc_cli_debugger/cli/
### python/ (OV-owned shared bridges, Q4)
  swipl_bridge.py -> python/omega_vision/prolog_bridge.py
  image_codec.py -> python/omega_vision/image_codec.py
  gpt_bridge.py  -> python/omega_vision/gpt_bridge.py
### python/object_memory/** (historical, Q8)
  Final-name+layout from birth. File-level map = rename detection of c509dc49 (object_memory->omega_vision)
  composed with ee8a9abb (flat->subpackages), e.g.:
    models.py->core/models.py, memory.py->core/memory.py, prediction.py->core/prediction.py,
    learning.py->core/learning.py, recognition.py->core/recognition.py, store.py->core/store.py,
    forms.py->forms/forms.py, adapters.py->adapters/adapters.py, providers.py->adapters/providers.py,
    sprite.py->adapters/sprite.py, capture.py->runtime/capture.py, catalog.py->runtime/catalog.py,
    replay.py->runtime/replay.py, integration.py->runtime/integration.py, transcript.py->runtime/transcript.py,
    calibration.py->evaluation/calibration.py, benchmark.py->evaluation/benchmark.py,
    acceptance.py->evaluation/acceptance.py, recognition_benchmark.py->evaluation/recognition_benchmark.py,
    environment_fixtures.py->environments/environment_fixtures.py, __init__.py->__init__.py
  (authoritative map generated by script from git -M data at replay time; subpackage __init__.py files
   appear when ee8a9abb's replay reaches them)
  Facade (old python/omega_vision/ package incl. _future.py, forms/base.py, accelerators/, adapters/grid ...)
  DROPPED from replay; facade-only commits skipped; mixed commits keep non-facade hunks.
### python/ KEEP
  worldworkbench/**, project_paths.py, multillm_runner.py, unsloth_studio.py, collection_operations.py,
  visual_image_diff_operations.py, workflow_operations.py, workflow_operation_editor.py, llm_*.py, __init__.py
### workbench/frontend/ -> frontend/
  Vision pages/styles -> frontend/packages/omega_vision_ui/src/:
    components/{VideoImportPage,Arc3B1B2PipelinePage,Arc3PromptPrologPage,Arc3PlayPage,
    RecognitionDemosPage,VisualImageDiffPage}.tsx + styles/{video_import,arc3_prompt_prolog,
    visual_image_diff,...matching}.css
  Everything else -> frontend/apps/workbench/ (same relative layout: src/, index.html, package.json,
    package-lock.json, tsconfig*.json, vite.config.ts, vite.ws_collab.config.ts)
  shared_ui/ package: created in post-replay refactor (not during replay)
  apps/omega_vision/ shell: post-replay scaffold commit (Q5)
### workbench/plugins/ -> plugins/
  plugins.json, README.md, .gitignore, web_proxy/** (tracked history)
  Untracked nested repos (emullm, ws_audio, ws_collab, codex_cli, coplex, coplex_stdpy, mailbox_chat,
  HIDE_*) -> physical move to plugins/ after replay approval; never enters replayed history.
### workbench/workspaces/ -> workspaces/
  All 17 workspaces keep names/relative layout EXCEPT:
  arc3_random_player/data/** -> data/omega_vision/** (tracked files MOVE in history; relative org preserved:
    arc3_games/, vision_frames/, video_import/; untracked recognition_reduce/ etc. move post-replay)
  arc3_random_player/knowledge/object_memory.db.pl -> data/omega_vision/knowledge/ (untracked, post-replay)
### workbench/docs/ -> docs/  (design/, todo/, 3 root files; no collisions with existing docs/)
### workbench root files
  workbench/README.md -> docs/WORKBENCH.md (tentative-approved)
  workbench/run_demo.bat, run_demo.sh -> workbench_api_server/scripts/
  workbench/scripts/** -> workbench_api_server/scripts/
  workbench/config (historical) -> workbench_api_server/config/
### Tests -> six+1 buckets (TEST_MOVE at replay)
  tests/omega_vision/: test_phase2_*, test_omega_vision_sow_forms, test_object_memory_contracts,
    test_object_memory_rest_roundtrip?, test_symbolic_arc_*, test_turtle_normalize, test_arc3_capture_observers, ...
  tests/omega_vision_api/: test_video_import_*, test_arc3_play_* , registry/phase3/recognition API tests
  tests/workbench_api/: workspace/resource/operation/prompt/model/policy/plugin/service/system/
    workflow-engine/docs/mailbox tests + 5 embedded workbench/server/test_*.py + repo-hygiene tests
  tests/arc_cli_debugger/: action-tree, interactive-runner, runner-path, windows smoke tests (Q12)
  tests/plt/: native .pl tests + run_tests.pl
  tests/workbench_ui/, tests/omega_vision_ui/: start empty
  (authoritative per-file list generated by script; ambiguous files flagged for review at replay PR)
### Historical-only paths (deleted before tip)
  examples/, prompts/, action_trees/, tic_tac_toe_learner/, .llm_responses/, webui-legacy variants,
  root *.md removed files: replay at HISTORICAL paths (they have no final location; they die where they died),
  EXCEPT files matching a mapped family (e.g. historical workbench/** files follow the family mapping).
### KEEP at root (Phase-4 path repairs only)
  README.md, AGENTS.md, CODEX_TODO.md, DEBUGGER.md, FILE_TREE.md, KAGGLE.md, LICENSE, Makefile,
  README_WINDOWS.md, README_WEB_TERMINAL_FIX.md, SOW_*.md, TODO.md, pyproject.toml, requirements.txt,
  run_workbench.bat, workbench.workspace.json, .github/**, .idea/, .run/, .codex/, config/, scripts/(rest),
  notebooks/, agent/, data/{object_memory,object_memory_demo,recognition_demo_parts}, docs/(existing),
  _sow.txt, _ingest_reduce_seed.py -> scripts/ (tentative), .gitignore/.gitattributes/.env.example
  webui gone (moved to debugger). tools/ does not exist (hint checked; nothing found).

## Replay mechanics (Phase 2/3, pending final go)
- Custom replay script (git fast-export/commit-tree based) over first-parent+merges of main,
  applying this mapping file-by-file; COPY_HISTORY files written to both blobs per commit.
- Preserve author/committer, dates, messages, merge topology; skip facade-only empty commits.
- Emit original->reconstructed commit map (CSV) + divergence log for COPY_HISTORY pairs.
- New branch (e.g. history/final-layout) in a scratch clone; NEVER force-push main; live server untouched.
- Phase 4 path-repair commits follow the approved seven-group order from the earlier instructions.
