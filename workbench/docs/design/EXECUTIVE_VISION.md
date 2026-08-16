[← Back to repository README](../../../README.md)

# Executive Vision

## The thesis

Large language models can already perform remarkable work. Our premise is that their useful capability is determined not only by model size or frontier status, but also by the quality of the informational and operational environment around the model.

The MeTTaSymbolicLearnerWorkbench supplies that environment.

Instead of asking one model to understand a large problem, invent a plan, remember every relevant fact, choose tools, write code, monitor itself, recover from mistakes, and judge completion in one loosely controlled conversation, the workbench provides explicit infrastructure for each responsibility. It gives models a semantic workflow language, typed values, AtomSpace-backed memory, operation catalogs, bounded control flow, evidence and provenance, preflight validation, runtime policies, implementation alternatives, and structured feedback.

This is deliberate micromanagement in service of greater capability.

## Why it matters

An unconstrained model spends part of its intelligence reconstructing missing infrastructure: remembering prior decisions, deciding what to do next, discovering available tools, tracking intermediate values, noticing loops, checking its own work, and recovering context after errors. Those tasks consume attention, tokens, time, and reliability.

The workbench externalizes them.

Models receive the information needed for the current decision, an explicit contract, permitted operations, relevant memory, validation results, and a bounded next objective. The system retains durable state and evidence so the model does not have to simulate a database, workflow engine, debugger, and project manager inside its prompt.

## The operating model

The workbench separates concerns that are usually collapsed into one model call:

1. A human or model writes an English semantic specification.
2. A constrained compiler produces a typed workflow using cataloged operations.
3. Preflight validates bindings, values, memory, branches, loops, reevaluations, and budgets.
4. Semantic operations resolve later to Python, Prolog, LLM calls, human input, services, or newly generated implementation children.
5. Runtime freezes those choices and records inputs, outputs, evidence, events, and policy decisions.
6. Validators, Coaches, or humans can redirect execution at explicit checkpoints.
7. Learned evidence returns to AtomSpace-backed memory without erasing its provenance.

Bicameral Mode CoT adds a controlled Thinker-and-Coach relationship. Depending on coaching cadence, the Coach can prepare the Thinker's questions and considerations once, update them at milestones, respond after every structured work product, or intervene only when uncertainty, contradiction, changed evidence, or validation failure triggers reevaluation.

## The model-efficiency hypothesis

Frontier models are valuable, but using the strongest available model for every decision is expensive and often unnecessary. Many subtasks become tractable for smaller, older, local, or otherwise less capable models when the workbench provides:

- narrowly scoped objectives;
- complete relevant context;
- typed inputs and outputs;
- prepared reasoning plans;
- Coach guidance;
- persistent external memory;
- explicit tool and operation choices;
- bounded retry and reevaluation loops;
- deterministic validation;
- escalation when confidence or capability is insufficient.

Our hypothesis is testable: a well-orchestrated collection of non-frontier models can outperform a single unstructured frontier-model call on end-to-end reliability, reproducibility, cost, recoverability, and—on suitable workloads—task quality.

This is not an assumption that weaker models always beat stronger ones. It is a systems claim: orchestration, memory, semantics, evidence, and verification can matter as much as raw model capability. The workbench should measure the claim per workflow and route genuinely difficult decisions to frontier models only when evidence shows they are needed.

## What success looks like

Success is not merely producing an impressive answer once. A successful system can explain what it attempted, reproduce which resources and implementations it used, show why memory changed, identify where validation failed, resume without losing state, substitute implementations, compare model policies, and improve from retained evidence.

The long-term objective is a model-independent cognitive workbench: a place where models of different ages, sizes, vendors, modalities, and implementation styles can collaborate through durable semantic artifacts. Better models should improve the system, but the system should not depend on any one model remaining the frontier.

The core bet is simple:

> Give language models better structure, better memory, better tools, better evidence, and better supervision, and they can do more than model capability alone would predict.
