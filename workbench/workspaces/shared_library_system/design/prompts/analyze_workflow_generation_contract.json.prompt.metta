(
  (kind prompt)
  (id workflow.analyze_generation_contract.json)
  (label "Analyze Workflow Generation Contract / JSON")
  (version 1)
  (targets ([]
    generic-chat
    reasoning-chat
  ))
  (implements (
    (workflow.analyze_generation_contract (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (text ([]
    "Analyze english_specification and produce one complete Generation Contract plus one candidate Workflow in exactly one response. "
    'Revise existing_workflow as the base. Use only exact operation IDs and typed ports from effective_operation_catalog, only exact existing Datatype IDs and relationships from effective_datatype_catalog, only exact existing Workflow IDs from effective_workflow_catalog, and conform the candidate to workflow_schema.'
    "generation_steps is the user-composed ordered list. "
    'Each item has name and visibility plus optional promptId and modelId routing declarations. '
    'After an occurrence produces its value, visibility.peers=true makes that value available as context to subsequent occurrences with a different name; visibility.peers=false prevents those other output types from seeing it. '
    'visibility.updates=true makes that value available as the old value to a subsequent occurrence with the same name, which may revise it; visibility.updates=false makes the later same-type occurrence generate without seeing that old value. '
    'Inside a simultaneous group, peers=true makes the value shared batch context for other output types in that group. '
    'These two visibility scopes completely replace the former new/reuse/preserve/hide mode. '
    'Every listed occurrence executes; a repeated name appends another generation stage. '
    'name is summary, memory, checklist, outputs, rules, englishsteps, steps, workflow, libops, matchops, inventops, codeops, promptops, libdt, matchdt, inventdt, codedt, libwf, matchwf, inventwf, codewf, or group; names may repeat. '
    'Process every item in the exact listed order. Resolve promptId only against effective_prompt_catalog and use that prompt resource as additional instructions for that occurrence. '
    'Treat modelId as explicit routing provenance for that occurrence; do not invent capabilities or results for a different model. '
    'A group item contains a nested steps array; generate or revise those nested outputs together as one simultaneous batch without imposing an internal section order. '
    'An empty group means all twenty-one outputs. The group visibility, promptId, and modelId are batch defaults, and each nested step can override them for that output. '
    'Echo the processed top-level name sequence, including group, as order_used so the workbench can audit the trial. '
    'Do not silently reorder stages into a preferred sequence.'
    "generation_contract.summary is a concise task summary string. "
    'generation_contract.memory is an array of objects with name, datatype, and requirement. '
    'generation_contract.checklist is an array of independently testable acceptance statements. '
    'generation_contract.outputs is an array of required output statements. '
    'generation_contract.rules is an array of validation, safety, termination, and resource-grounding rules. '
    'generation_contract.englishsteps is an array of readable step objects with stepId, label, purpose, dependsOn, and controlFlow. '
    'generation_contract.steps is an array of complete formal Workflow step objects conforming to workflow_schema. '
    'generation_contract.libops is an array of relevant existing Operation prototypes copied from effective_operation_catalog with operationId, label, description, typed inputs, and typed outputs. '
    'generation_contract.matchops is an array of objects with requirement, operationId, status, and rationale; status is matched or unresolved, and unresolved entries have an empty operationId. '
    'generation_contract.inventops is an array of proposed Operation contracts with requirement, operationId, description, typed inputs, typed outputs, constraints, and status; status is proposed and these entries must not be represented as existing resources. '
    'generation_contract.codeops is an array of proposed implementation contracts with operationId, implementationId, implementationType, description, entrypoint, typed inputs, typed outputs, constraints, and status; status is proposed and these entries must not be represented as implemented code or existing resources. '
    'generation_contract.promptops is an array of proposed prompt resources for new LLM-backed Operations with operationId, promptId, label, instructions, inputBindings, outputContract, modelRequirements, and status; deterministic implementations do not receive unnecessary prompts. '
    'generation_contract.libdt is an array of relevant existing Datatype resources copied from effective_datatype_catalog with datatypeId, kind, label, and description. '
    'generation_contract.matchdt is an array of objects with requirement, datatypeId, representationId, concreteDatatypeId, status, and rationale; status is matched or unresolved. '
    'generation_contract.inventdt is an array of proposed semantic Datatype contracts with requirement, datatypeId, kind, description, parents, constraints, and status. '
    'generation_contract.codedt is an array of proposed representation/concrete contracts with datatypeId, representationId, concreteDatatypeId, encoding, validator, conversionOperations, constraints, and status. '
    'generation_contract.libwf is an array of relevant existing Workflow resources copied from effective_workflow_catalog with workflowId, label, description, typed inputs, and typed outputs. '
    'generation_contract.matchwf is an array of objects with requirement, workflowId, status, and rationale. '
    'generation_contract.inventwf is an array of proposed Workflow contracts with requirement, workflowId, description, typed inputs, typed outputs, constraints, and status. '
    'generation_contract.codewf is an array of build reports with workflowId, stepIds, operationIds, datatypeIds, unresolvedOperations, unresolvedDatatypes, and status. '
    'Proposed Datatype and Workflow entries have status proposed and must not be represented as existing resources or implemented code.'
    "The checklist must cover every explicit behavior, initialization, loop condition, termination condition, output, and non-negotiable constraint in the English specification. "
    'Memory entries must be justified by the specification rather than invented implementation details. '
    'Preserve conflicts and ambiguity as checklist or validation rules instead of silently resolving them.'
    "Return strict JSON with exactly three top-level properties: generation_contract, workflow, and order_used. "
    'generation_contract contains summary, memory, checklist, outputs, rules, englishsteps, steps, libops, matchops, inventops, codeops, promptops, libdt, matchdt, inventdt, codedt, libwf, matchwf, inventwf, and codewf. '
    'workflow is one complete candidate Workflow object, not a patch or a list of steps. '
    'Return no Markdown, comments, ellipses, private hidden chain-of-thought, or explanatory fields.'
  ))
)
