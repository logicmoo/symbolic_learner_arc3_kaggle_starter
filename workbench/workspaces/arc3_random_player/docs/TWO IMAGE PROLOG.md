# B1 -> B2 Pipeline UI (single-stack)

Route: `arc3B1B2Pipeline`  
Renderer: `arc3_prompt_prolog`  
Visible stack columns: `B only`  
Default timeouts: `max_primary_secs=1800`, `max_loop_secs=1800`

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ LEFT COLUMN: INPUTS                                                        │
│  1) B1/B2 Inputs                                                           │
│     - Entry/context panel for setup+image flow.                            │
│                                                                             │
│  2) Combined Prompt Contract                                               │
│     - Full extraction contract reference text.                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CENTER COLUMN: B1 THEN B2                                                  │
│  1) Run B1 Then B2                                                         │
│     - G · SHARED THING: page/global model resolution                       │
│     - ALL-STACK: contains only STACK B on this page                        │
│                                                                             │
│     STACK B                                                                │
│       SETUP B                                                              │
│       - Setup list, commands, before/after paths, previews                │
│                                                                             │
│       RUNNER B1 (removal stage)                                            │
│       - Prompt: remove_smallest_object                                     │
│       - Produces many_objects_1..n-style outputs (plus compatibility keys) │
│       - Loop control is driven by prompt exit_value                        │
│                                                                             │
│       RUNNER B2 (regeneration stage)                                       │
│       - Prompt: regenerated_identities_from_many_objects                   │
│       - Consumes many_objects inputs and all selected INPUT_FILES          │
│       - Returns current_identities + regenerated_identities                │
│       - Loop control is driven by prompt exit_value                        │
│                                                                             │
│       Per-runner controls                                                   │
│       - INPUT_FILES source picker                                           │
│       - PRIMARY_MODEL / LOOP_MODEL                                          │
│       - Prompt names + prompt text                                          │
│       - LIMITS: max_primary_secs / max_loop_secs / max_iterations           │
│       - Run Primary / Run Loop / Run Until Exit                             │
│       - LOOP_FILES / RAW_PARSED / REMOVAL_IMAGES / OUTPUT_FILES             │
│                                                                             │
│  2) B1/B2 Output Files                                                     │
│     - Runner output selector + parsed output files + history               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ RIGHT COLUMN: SOURCE DETAILS                                               │
│  1) Current Page Specification                                             │
│     - Editable workflow_page JSON source                                   │
│  2) Raw Model Response                                                     │
│     - Exact model text + debug trace/log content                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Execution Summary

1. Run **B1** to generate removal artifacts (`many_objects_n` style outputs).
2. Run **B2** to regenerate and merge identities from those outputs + input files.
3. Continue/stop by prompt `exit_value` (`next_iteration`, `loop_complete`, etc.).