[← Back to documentation contents](contents.md)

# Workbench System Overview

The MeTTa Symbolic Learner Workbench is a blackboard workspace where a human and AI systems build, inspect, and run tool-using workflows together. It plays a role similar to a coding agent: the human directs and reviews the work, while AI and symbolic systems help construct and execute it. Here, however, the product is a reusable workflow for solving or learning a problem rather than source code alone.

## From intent to execution

```text
Goal
  -> Planning Strategy (human, PDDL, LLM, or another planner)
  -> Workflow / Plan (ordered or graph-structured planned steps)
  -> Operations (what each step does)
  -> Implementation + Source Code (how each Operation runs)
  -> Events, States, Artifacts, and Logs
```

A **Planning Strategy** describes how a plan should be produced. A **Workflow** is the resulting executable plan. For a PDDL user, a Workflow corresponds to a grounded PDDL plan; the workbench retains its planner, domain, problem, and provenance rather than imposing different planning terminology.

An **Operation** is a typed semantic contract: what the step does, its inputs, and its outputs. An implementation says how it is done and binds the Operation to source such as a Prompt, Prolog, MeTTa, or Python. Systems and Models provide the execution backends that run that source.

## Where things are edited

| Area | Editors and purpose |
| --- | --- |
| Workspace | Overview, Goals, Planning Strategies, and Workflows |
| Capabilities | Operations; Source Code (Prompts, Prolog, MeTTa, Python); Systems; Models; Datatypes; Policies |
| Knowledge | imported Data, named AtomSpaces, and durable Artifacts |
| Runtime | Goal Runs, Executions, Events, States, and Logs |
| System | documentation, model policy, benchmarks, managed processes, and workspace settings |

Prompts are source code for LLM-backed Operation implementations; they are not model configuration. Models select inference capabilities, while Model Presets specialize invocation parameters without changing the Operation being performed.

## Blackboard behavior

Operations read typed values and Atoms from named AtomSpaces and write results back as Atoms, files, or runtime records. AtomSpace changes produce Events. This shared, inspectable state lets humans, planners, LLMs, Python, SWI-Prolog, and MeTTa cooperate without hiding intermediate reasoning or provenance.
