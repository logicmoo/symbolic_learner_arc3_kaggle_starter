# Model Runtime Usage and Benchmarking Policies

[Back to repository README](../../../README.md)

Build the **Model Runtime Usage and Benchmarking Policies** page in the **MeTTaSymbolicLearnerWorkbench**.

## Implementation Status

The active page is backed by real workspace resources and the model-policy API. It currently provides vendor/model intent editing, inherited vendor overrides, dynamic provider-property columns, composable filters, sortable columns, frozen identity/policy columns, horizontal and vertical scrolling, visible-row selection, concurrent model probes, health observations, effective runtime and benchmark eligibility, prompt-profile references, persisted benchmark execution/results, and filesystem load/save.

Remaining work is intentionally narrower:

- optionally embed vendor creation and backend discovery instead of using the current direct link to the Models editor's backend creation, discovery, selection, and overwrite import tools;
- refine multi-column sorting if future catalog usage reveals additional ordering needs (Shift+click already composes sort keys);
- optionally remove legacy read compatibility for the former benchmark-policy `promptProfiles` field after existing workspaces have migrated to `modelPresets`;
- optionally add comparison overlays or aggregation controls beyond the current persisted-result time-series chart and exact chronological result rows.

The requirements below remain the acceptance specification. Existing completed behavior must not be replaced with mock data.

This page is the central place where the user controls which vendors and models are wanted, which are allowed at runtime, which are benchmarked, which are currently healthy, and how reusable Model Presets are compared across enabled models.

The page should closely follow the existing mockup.

## Page Purpose

The page must keep three concepts separate:

```text
User Policy
    ↓
Live Health / Availability
    ↓
Effective Runtime Eligibility
```

Do not use one field called “Available” to mean all three things.

A model or vendor can be:

```text
Wanted = OFF
Health = Online
```

meaning it works but the user does not currently want it used.

Likewise:

```text
Wanted = AUTO
Health = Slow
Effective = Temporarily Disabled
```

meaning the user allows dynamic use, but runtime policy has excluded it because it is currently too slow.

---

# Top-Level Layout

Use the existing left navigation and overall dark/purple visual style.

The page title is:

```text
Model Runtime Usage and Benchmarking Policies
```

The main layout should be:

```text
+------------------------------------------------------------------+
| Page Title                                      Global Ping Tools |
+------------------------------------------------------------------+
| Tabs                                                             |
+------------------------------------------------------------------+
| Vendors              | All Models                    | Summary    |
|                      |                               |            |
+------------------------------------------------------------------+
| Model Presets        | Benchmark Matrix              | Performance|
|                      |                               | Overview   |
+------------------------------------------------------------------+
| Testing Rules / Policy Controls                                 |
+------------------------------------------------------------------+
```

Do not include a separate legend row between the second row and Testing Rules.

---

# Global Ping Controls

Near the top-right of the page, provide:

```text
[ Ping All ]
[ Ping Wanted ]
[ Ping Auto ]
[ Ping Unwanted ]
[ Refresh Status ]
```

These operations should run concurrently.

A slow or failed ping must not prevent the remaining models/vendors from being checked.

Health checks should be asynchronous and independently update each row.

---

# Vendors Frame

The Vendors frame should contain:

```text
[ + Add Vendor ]
[ Filesystem Load ]
[ Filesystem Save ]

Ping:
[ All ] [ Wanted ] [ Auto ] [ Unwanted ]
```

Columns should include at least:

```text
Vendor
Wanted
Benchmark
Runtime
Health
Latency
Model Count
Actions
```

Use these semantics:

```text
Wanted
    ON
    AUTO
    OFF

Runtime
    ON
    AUTO
    OFF

Benchmark
    ON
    AUTO
    OFF

Health
    Online
    Slow
    Offline
    Unknown
    Rate Limited
    Authentication Error
    Error
```

Health is observed state.

Wanted/Runtime/Benchmark are policy.

These must not be conflated.

## Vendor Interaction

Single-click a vendor:

```text
select vendor
show/filter its models
```

Double-click a vendor:

```text
1. Ping vendor
2. Test authentication / endpoint
3. Pull current model list from vendor
4. Merge model list with locally known models
5. Refresh known model properties
6. Select vendor
7. Show vendor models
```

Provide an explicit action equivalent to this as well:

```text
[ List / Refresh Models ]
```

---

# All Models Frame

The **All Models** table is the central live model registry.

It must support arbitrary provider/model properties and therefore must use both vertical and horizontal scrolling.

Important rule:

```text
Vertical scrollbar = model rows
Horizontal scrollbar = model properties
```

Do not use pagination as the primary way of limiting displayed models.

If pagination already exists, remove or de-emphasize it. Model count visible at once should be determined by frame height and vertical scrolling.

---

# Frozen Columns

Freeze the policy/identity columns on the left side while horizontally scrolling.

Freeze:

```text
Vendor
Model Name
Wanted
Runtime
Benchmarked
Health
```

These must remain visible at all times.

The rest of the properties horizontally scroll.

Conceptually:

```text
FROZEN
---------------------------------------------------------
Vendor | Model | Wanted | Runtime | Benchmarked | Health

SCROLLABLE
---------------------------------------------------------
Type
Vision
Audio
Video
Multimodal
Function Calling
Tool Use
Structured Output
JSON Mode
Image Input
Image Output
Code Execution
Reasoning
Streaming
Embeddings
Context Window
Max Output
Input Cost
Output Cost
Cached Input Cost
Average Latency
Failure Rate
Benchmark Score
Last Ping
Last Successful Call
Provider-specific properties
...
```

Do not hard-code the scrollable list to only these properties.

The table should be able to display arbitrary properties discovered from vendor model metadata.

---

# Model Filters

Across the top of **All Models**, provide composable filters.

At minimum:

```text
Vendor
Type
Modality
Capabilities
Wanted
Runtime
Benchmarked
Health
Search
```

Example controls:

```text
Vendor:       [ All Vendors ▼ ]
Type:         [ All Types ▼ ]
Modality:     [ All Modalities ▼ ]
Capabilities: [ All Capabilities ▼ ]

Wanted:       [ All | ON | AUTO | OFF ]
Runtime:      [ All | ON | AUTO | OFF ]
Benchmarked:  [ All | ON | AUTO | OFF ]

Health:
[ All | Online | Slow | Offline | Unknown | Rate Limited | Error ]

[ Search models... ]
```

Filters must compose.

Example:

```text
Vendor = Local / Self Hosted
Wanted = AUTO
Vision = Yes
Health = Online
Runtime = ON
```

must show only matching models.

---

# Model Ping Controls

Inside the All Models frame provide:

```text
Ping:
[ All ]
[ Wanted ]
[ Auto ]
[ Unwanted ]
[ Selected ]
```

Important behavior:

* `Ping All` checks everything visible/known.
* `Ping Wanted` checks ON candidates.
* `Ping Auto` checks AUTO candidates.
* `Ping Unwanted` checks OFF candidates intentionally.
* `Ping Selected` checks only selected rows.

The ability to ping unwanted models is deliberate.

The user may temporarily disable something because it is slow or undesirable but still wants to know whether it has recovered.

---

# Sort Behavior

Every column header should be sortable.

Behavior:

```text
first click  = ascending
second click = descending
```

Support multi-column sort if practical:

```text
Shift + Click = add secondary sort
```

Example:

```text
Health: Online first
Latency: fastest first
Benchmark Score: highest first
```

Sorting should work on dynamic/provider-specific columns when possible.

---

# Policy vs Health vs Effective State

Internally model these separately.

Example:

```text
Wanted:
    ON | AUTO | OFF

Runtime:
    ON | AUTO | OFF

Benchmarked:
    ON | AUTO | OFF

Health:
    Online | Slow | Offline | Unknown | RateLimited | Error

EffectiveRuntime:
    Enabled | Disabled | TemporarilyDisabled

EffectiveBenchmark:
    Enabled | Disabled | TemporarilyDisabled
```

Example:

```text
Wanted: AUTO
Runtime: AUTO
Health: Slow
EffectiveRuntime: Disabled
Reason: latency threshold exceeded
```

Do not rewrite the user's `Wanted=AUTO` value just because the model becomes slow.

Likewise:

```text
Wanted: ON
Health: Rate Limited
EffectiveRuntime: Temporarily Disabled
Reason: retry_after=43 seconds
```

This distinction is important.

---

# Slow Model Behavior

If a model becomes too slow:

```text
1. mark health as Slow
2. record measured latency
3. optionally exclude it from effective runtime candidate selection
4. continue pinging/checking all other candidates
5. do NOT change its user policy automatically
```

The runtime may quietly decide not to use the model while preserving the user's ON/AUTO/OFF setting.

Thresholds should be configurable later.

---

# Model Presets Frame

Restore and preserve a **Model Presets** panel.

Example presets:

```text
Light
Deep
Deterministic
Long Output
Vision High Detail
```

Model Presets inherit a Model (or another Model Preset) and override invocation defaults such as temperature, reasoning effort, timeout, token budget, or image detail. They remain prompt-free.

They are not vendor identities and they are not prompt composition.

Prompt Profiles are separate, first-class prompt-composition resources. They express reusable approaches such as Object-First or Scene-Graph without selecting a vendor or changing model invocation defaults. An LLM Operation may bind one or more profiles through `bindings.promptProfiles`, then append any directly bound prompts.

Provide model-preset creation and editing through the rich Models hierarchy:

```text
[ + Add Model Preset ]
```

---

# Benchmark Matrix

Restore and preserve the **Benchmark Matrix** panel.

Conceptually:

```text
Model Presets × Enabled Models
```

Rows:

```text
Model Presets
```

Columns:

```text
Enabled Models
```

Cells should indicate states such as:

```text
Enabled & Compatible
Enabled but Limited
Disabled
Not Compatible
```

The benchmark framework should eventually profile:

```text
Model Preset
× Model
× Input Class
```

The benchmark cross product now treats Model Presets and Prompt Profiles as independent dimensions. Each result records both `modelPresetId` and, when configured, `promptProfileId`; the matrix can facet by Prompt Profile without folding prompt composition into model invocation settings.

Claude vs OpenAI should emerge from benchmark results, not be encoded into prompt identity.

---

# Performance Overview

Restore and preserve the **Performance Overview (Historical)** panel.

It should visualize historical benchmark results.

Support a metric selector, for example:

```text
Overall Score
Accuracy
Latency
Cost
Success Rate
Token Usage
```

This can initially be a simple grouped bar chart using mock or existing benchmark data.

The important purpose is to compare prompt/model combinations historically.

---

# Testing Rules

Keep the Testing Rules row at the bottom.

At minimum:

```text
Max Cost per Benchmark Run
Max Total Monthly Budget
Allow Paid Models
Allow Multimodal Models
Allow Local Models
Allow Experimental Models
```

Each policy should be editable.

Example:

```text
Max Cost per Benchmark Run
$25.00

Max Total Monthly Budget
$200.00

Allow Paid Models
Enabled

Allow Multimodal Models
Enabled

Allow Local Models
Enabled

Allow Experimental Models
Disabled
```

Keep:

```text
[ Save Policy ]
```

as the primary save action.

---

# Filesystem Persistence

Vendor and model frames must support filesystem persistence.

Vendor frame:

```text
[ Filesystem Load ]
[ Filesystem Save ]
```

Model frame should also support:

```text
[ Filesystem Load ]
[ Filesystem Save ]
[ List / Refresh Models ]
```

Persist at least:

```text
vendor configuration
model configuration
Wanted state
Runtime state
Benchmark state
manual overrides
known capabilities
cached metadata
```

Live health should generally be refreshed rather than treated as authoritative persisted state, though last-known values may be cached.

---

# Suggested Internal Data Shape

Do not bind the UI directly to provider-specific schemas.

Normalize common fields but retain arbitrary vendor metadata.

For example:

```metta
(
  (id openai:gpt-5.6-deep)
  (vendorId openai)
  (modelId gpt-5.6-deep)
  (name "GPT-5.6 Deep")
  (policy (
    (wanted on)
    (runtime on)
    (benchmark on)
  ))
  (health (
    (status online)
    (latencyMs 180)
    (lastPing ...)
    (lastSuccess ...)
    (failureRate 0.01)
  ))
  (effective (
    (runtime true)
    (benchmark true)
    (reason null)
  ))
  (capabilities (
    (vision true)
    (audio true)
    (multimodal true)
    (tools true)
    (functionCalling true)
    (jsonMode true)
  ))
  (limits (
    (contextWindow 1000000)
    (maxOutput 32000)
  ))
  (pricing (
    (input 0.12)
    (output 0.48)
  ))
  (properties (
    ("... arbitrary vendor properties ..." ...)
  ))
)
```

The `properties` dictionary is important because the All Models grid needs to grow beyond the normalized schema.

---

# Key Architectural Principle

The page should make this distinction visually and structurally obvious:

```text
What the user wants
        ≠
What is reachable
        ≠
What runtime currently chooses
```

More formally:

```text
USER POLICY
    Wanted / Runtime / Benchmarked
             │
             ▼
LIVE OBSERVATION
    Health / latency / errors / limits
             │
             ▼
RUNTIME DECISION
    Effective eligibility
```

The user should be able to intentionally keep a healthy model OFF, keep an unreliable model AUTO, temporarily route around a slow model, and still ping every category independently.

The page is therefore more than a settings page.

It is the **live model registry, model policy editor, health monitor, prompt/model benchmarking dashboard, and runtime eligibility controller** for the MeTTaSymbolicLearnerWorkbench.
