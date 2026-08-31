(
  (kind prompt)
  (id workflow.plan_memory_and_values.default)
  (label "Plan Workflow Memory and Values / Default")
  (version 1)
  (targets ([]
    generic-chat
    reasoning-chat
  ))
  (implements (
    (workflow.plan_memory_and_values ())
  ))
  (text ([]
    "Plan the memory model and values model for the supplied complete semantic workflow. \nDo not implement operations and do not invent ports, steps, or resources. \nUse only declared workflow inputs, step outputs, bindings, control edges, and supplied datatype catalog entries."
    "For the memoryModel, classify every retained item as transient step state, iteration state, game or chapter state, run state, workspace learning memory, or durable cross-run memory. \nUse the canonical fields atomspace_scope, atomspace_scope_key, atomspace_cell, atomspace_atom, change_mode, and evidenceLink. \nDeclare datatype, initial atom source, writers, readers, change rule, persistence location, retention policy, provenance, and reset conditions."
    "Separate operational state from learned evidence. \nDurable learning memory must retain the observation or assessment that justified each update and must never silently overwrite contradictory evidence. \nIdentify secrets or credentials as references only; never copy their values into workflow memory."
    "For the valuesModel, enumerate every workflow input, produced output, alias, and final output. \nDeclare producer step and port, consumer steps and ports, datatype, scope, cardinality, optionality, default, lineage, and whether the value is immutable, accumulated, merged, or overwritten."
    "Infer iteration groups when the same logical output name is written again or when a bounded backward control edge repeats a region. \nValues created between repeated writes belong to that iteration group unless the workflow explicitly gives them a wider scope. \nRecord group id, loop operation, boundary steps, iteration key, retained values, reset values, accumulated values, and values exported after the loop."
    "Detect ambiguous writers, reads before production, unreachable values, accidental shadowing, incompatible datatypes, outputs that escape their scope, missing persistence, and memory that lacks provenance. \nReturn these as validationIssues with severity, affected IDs, evidence, and a concrete repair proposal."
    "Help preflight place reevaluation checkpoints where new values invalidate an earlier decision or where memory evidence changes an operation choice. \nIdentify trigger values, decision target, required retained context, and a finite reevaluation bound."
    "Return strict JSON with keys memoryModel, valuesModel, iterationGroups, reevaluationCheckpoints, validationIssues, and summary. \nDo not return Markdown, comments, ellipses, or private hidden chain-of-thought."
  ))
  (inheritsFrom (
    (workflow.plan_memory_and_values (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
