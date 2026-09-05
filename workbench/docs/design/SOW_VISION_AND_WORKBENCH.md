# Statement of Work: MeTTaSymbolicLearnerWorkbench and its Vision Subsystem

[Back to repository README](../../../README.md)

This document frames what the workbench is as a Statement of Work (SoW), at two
levels: the overall program (the workbench as a neurosymbolic experiment desktop)
and the vision subsystem (the ARC recognition / perception / sequence-induction
pipeline). It is a descriptive SoW of work already delivered, suitable for reuse
in proposals and RFP responses that require statistical reporting.

---

## 1. Program Level: MeTTaSymbolicLearnerWorkbench

### Objective
Deliver a filesystem-backed *neurosymbolic experiment desktop* where every
artifact of a learning system is a first-class, versioned, inspectable resource
that a human and an AI can co-edit and execute: goals, plans, workflows,
operations, datatypes and representations, source (prompts / Prolog / MeTTa /
Python), models and backends, atomspaces, runs / executions / events / states /
logs, policies, and benchmarks.

### Scope of Work
- A React/Vite workbench over a FastAPI backend, organized as five navigation
  groups: WORKSPACE, CAPABILITIES, KNOWLEDGE, RUNTIME, SYSTEM.
- Hierarchical artifact editors: a specification parent, concrete alternatives
  beneath it, a preferred/default selector, persistent tabs, dirty markers,
  split comparison, rich per-artifact panels, raw MeTTa/JSON editing, tests,
  history, benchmarks, diff, logs, and a playground/run surface.
- Three independent bidirectional relationship graphs, never inferred from one
  another: `implements`/`implementedBy` (classification), `inheritsFrom`/
  `inheritedBy` (property inheritance with borrow/lend permissions), and
  `dependsOn`/`dependedOnBy` (effective enabled state). Abstract vs concrete
  status is *derived* from the current draft, resolved inheritance, and
  family-specific requirements, and is reversible.
- A lifecycle-first filesystem layout: `design/<kind>/` specs, `runtime/<kind>/`
  runs/events/states, `knowledge/data|artifacts/`, and `policies/`.
- All surfaces are backed by real filesystem/backend resources (no mocks).
- An OpenAI-compatible model relay (EmuLLM) that routes chat/completion requests
  to interchangeable model backends and to connected headless CLI worker agents
  by model masks, capability aliases, and a resolution-order routing DSL.

### Deliverables
The running application, the resource schemas and filesystem conventions, the
backend API contract, the family of rich editors, and the model-routing layer.

---

## 2. Design Rationale: Decomposing Skills Beyond One-Shot Reasoning

The backend workbench exists to implement complex skills that are often beyond
what a single one-shot LLM call can do reliably. Even a premium model that
usually answers a hard task in one shot will, on the occasional "weird"
instance, silently fail; a monolithic one-shot approach has no way to notice
where or why.

The workbench's answer is to treat a skill as a *decomposable pipeline*: instead
of betting the whole task on one long A-to-Z leap, the system breaks it into
shorter, lower-risk hops — A-to-D, D-to-E, E-to-P, P-to-Z — each of which is:

- **Lower variance.** A short, well-scoped hop is easier to get right than the
  full leap, so each step carries less risk.
- **Independently verifiable.** Every intermediate result can be checked,
  scored, and given a confidence, so a failure is localized to the hop that
  produced it rather than hidden inside one opaque answer.
- **Independently optimizable and swappable.** Each hop can use a cheaper model,
  a premium model, a Prolog rule, a Python routine, or a mix — chosen per step —
  and can be retried or replaced without redoing the whole task.
- **Measurable end to end.** Because each hop reports its own statistics, the
  whole skill produces a statistical report rather than a single pass/fail.

Once a skill is decomposed, each hop is then *optimized on its own* — and the
most valuable optimization is often to remove the LLM from that hop entirely.
When a sub-task is small and well understood, an LLM step can be replaced by a
deterministic implementation (a Prolog rule, a Python routine, a cached result),
which is cheaper, faster, reproducible, and free of the occasional silent
failure. Crucially, the LLM is frequently used to *write its own replacement*:
the system first has the LLM perform the hop (establishing the correct behavior
on real examples), then has it efficiently generate a deterministic Python (or
Prolog) implementation of that same hop. This distills an LLM step into
inspectable code and moves the model off the per-run hot path and into build
time — the LLM's cost is paid once to author the routine, not on every
inference. The workbench keeps the LLM only where it still earns its place, and
can run a deterministic implementation *alongside* the LLM so the two cross-check
each other. The vision subsystem is exactly this: perception that an LLM first
performed is now also done by a fully LLM-free symbolic recognizer, roughly two
orders of magnitude faster, running next to the LLM line for direct comparison.

This is why the workbench keeps operations, prompts, source, and models as
separate first-class resources with inheritance and alternatives: a skill is
assembled from interchangeable steps, and any step can be upgraded, downgraded,
or made fully deterministic as evidence demands. The vision subsystem described
next is the worked example of this decomposition.

---

## 3. Vision Level: Neurosymbolic Perception and Sequence Induction

### Objective
Turn a stream of ARC game frames into a *symbolic, probabilistic world model*:
objects, their identities over time, and the events and rules that explain change
— produced by two independent, directly comparable perception lines so their
agreement is itself a measurable signal.

### Worked Example: the Vision Skill as Optimized Hops

Rather than ask one premium multimodal call to go from raw frames all the way to
"here are the objects, what happened, and the rules" (the A-to-Z leap), the
vision skill is decomposed into hops, and each hop is implemented with the
cheapest reliable option. The inductive and statistical hops are coded directly
in Prolog/Python (deterministic), while the LLM version of the upstream
perception remains available so any hop can be run side-by-side for comparison:

| Hop | Sub-task | Chosen implementation | LLM version (for comparison) |
| --- | --- | --- | --- |
| import | frame + provenance (how/where imported) | Python, deterministic | n/a |
| perceive | PNG -> color grid -> connected-component regions -> topology | Python, deterministic | LLM multimodal extractor |
| group | regions -> objects (containment, common fate) | SWI-Prolog, deterministic | implicit in the LLM part list |
| represent | MeTTa part-graph + turtle geometry | deterministic | LLM emits the same schema |
| track | identity over time (carry-forward + gap re-identification, D4 rigid match) | Python/Prolog, deterministic | LLM's own stable labels |
| induce | events: moved / transformed / interacted / occluded / no-longer-occluded / consumed_or_taken / gone / new | **Prolog/Python, deterministic** | same inducer run over LLM-perceived parts, shown next to it |
| report | per-event confidence + occlusion horizon + support-ranked rules | **Python/Prolog, deterministic** | — |

The key point for this deliverable: the **inductive parts and the statistical
parts are directly coded** (Prolog/Python), so they are fast, reproducible, and
free of silent LLM failure — yet the **LLM line stays available** end to end, and
the same deterministic inducer can be pointed at either the deterministic parts
or the LLM parts, so every claim can be checked LLM-vs-deterministic on the same
frames.

### Scope of Work

1. **Dual perception, one schema.**
   - An LLM multimodal extractor.
   - A fully LLM-free symbolic recognizer: PNG decode to exact color grid,
     connected-component color regions, pixel topology (adjacency / enclosure),
     SWI-Prolog grouping, and emission of a MeTTa part-graph plus per-part turtle
     geometry. Both lines emit the identical schema so they can be diffed; the
     symbolic line runs roughly two orders of magnitude faster.

2. **Identity over time.**
   - Common-fate grouping under rigid D4 motion (translation plus flips and
     rotations): parts sharing a rigid transform are one object even while
     rotating.
   - Carry-forward naming so a matched part keeps its id/label across steps.
   - Gap re-identification: a returning region reclaims its identity across short
     occlusions, so identity survives a vanish-then-return.

3. **Event ontology with object permanence.** A single ontology, resolved across
   the whole sequence because a disappearance is only knowable once later frames
   provide evidence:
   `moved`, `transformed(X -> Y)`, `interacted(M, X)`, `occluded` (returns
   later, still there), `no-longer-occluded` (a seen-before part is visible
   again), `consumed_or_taken` (under a mover, never returns; picked up or eaten,
   unknown which), `gone` (no mover, never returns), `new`.

4. **Provenance.** Every imported image records how and where it came from in a
   provenance sidecar, surfaced per frame and baked into the symbolic text as
   `(transition frame_i + LEFT = frame_{i+1})` using authoritative ARC action
   labels (ACTION1..7 -> UP/DOWN/LEFT/RIGHT/SPACE/CLICK/UNDO).

5. **Statistical reporting.**
   - A tunable **occlusion horizon** (how many later frames of patience before a
     vanish is committed), with a baked backend default and a live UI override.
   - Per-event **confidence**: observed verdicts (`moved`, `occluded`,
     `no-longer-occluded`, `interacted`) are certain; `gone`/`consumed_or_taken`
     carry the forward evidence fraction (how much of the horizon window was
     actually observed without a return); `new` carries the backward evidence
     fraction; `transformed` carries a co-location pairing confidence. Confidence
     starts uncertain and firms toward 100% as evidence accumulates.
   - Confidence is written into the MeTTa facts (machine-readable, probabilistic
     symbolic output) and summarized per row in the UI (event count, mean
     confidence, count of still-provisional verdicts).

6. **Rule induction.** Support-ranked candidate rules (for example, "X moved onto
   Y then Y disappears") induced across the whole sequence, from either the
   Prolog parts or the LLM parts using the same source-agnostic inducer.

### Methodology
Perception in Python, grouping and inference in Prolog, symbolic representation
in MeTTa, and the LLM used only where it adds value and always cross-checked
against the deterministic line.

### Key Differentiators (statistical-reporting focus)
- Probabilistic symbolic facts with explicit, evidence-based confidence.
- A transparent, revisable belief model: verdicts are provisional and only
  resolved once subsequent frames are processed.
- Two independent estimators (symbolic vs LLM) whose concordance is a measurable
  statistic in its own right.
