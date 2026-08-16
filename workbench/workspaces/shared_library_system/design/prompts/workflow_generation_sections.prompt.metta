(
  (kind prompt)
  (id workflow.generation.summary)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName summary)
  (classificationId english_to_workbench.10.contract.010.summary)
  (produces ([] summary))
  (label "Generate Summary From Current Workflow Information")
  (description "Create or revise only the concise task summary portion of a Workflow Generation Contract.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.summary from english_specification. State the workflow goal, its essential behavior, its termination condition, and its final result concisely. Do not invent steps, Operations, memory, or constraints that the specification does not support. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.memory)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName memory)
  (classificationId english_to_workbench.10.contract.020.memory)
  (produces ([] memory))
  (label "Generate Memory Plan From Current Workflow Information")
  (description "Create or revise only the required memory and value plan portion of a Workflow Generation Contract.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.memory from english_specification, existing_workflow, and existing_memory_values_plan. For every retained value declare a stable name, datatype, requirement, scope, initialization, writers, readers, update behavior, reset behavior, persistence, and evidence linkage when supported. Use atomspace_scope, atomspace_scope_key, atomspace_cell, atomspace_atom, change_mode, and evidenceLink where those fields apply. Do not invent runtime state that is unnecessary for the specified workflow. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.checklist)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName checklist)
  (classificationId english_to_workbench.10.contract.030.checklist)
  (produces ([] checklist))
  (label "Generate Acceptance Checklist From Current Workflow Information")
  (description "Create or revise only the independently testable acceptance checklist for a generated Workflow.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.checklist as independently testable acceptance statements. Cover every explicit initialization, behavior, branch, loop condition, finite bound, termination condition, required side effect, final output, and non-negotiable constraint in english_specification. Each item must be observable or verifiable against the candidate workflow and its evidence. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.outputs)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName outputs)
  (classificationId english_to_workbench.10.contract.040.outputs)
  (produces ([] outputs))
  (label "Generate Output Requirements From Current Workflow Information")
  (description "Create or revise only the output contract required from the generated Workflow.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.outputs from english_specification. Name each required final output, datatype or shape when known, ordering or cardinality, producer responsibility, and evidence or provenance requirement. Distinguish final workflow outputs from transient step values. Do not add outputs merely because an Operation can produce them. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.rules)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName rules)
  (classificationId english_to_workbench.10.contract.050.rules)
  (produces ([] rules))
  (label "Generate Validation Rules From Current Workflow Information")
  (description "Create or revise only the validation, safety, termination, and grounding rules for Workflow generation.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.rules. Include finite loop and retry bounds, valid branch targets, reachable value bindings, datatype compatibility, declared memory provenance, operation-catalog grounding, required termination, and specification-specific safety constraints. Preserve genuine ambiguity as an explicit validation rule instead of silently resolving it. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.workflow)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName workflow)
  (classificationId english_to_workbench.10.contract.080.workflow)
  (produces ([] workflow))
  (label "Generate Workflow From Current Workflow Information")
  (description "Create or revise the complete semantic Workflow object after considering the other Generation Contract sections.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise the complete workflow output from existing_workflow as the base. Satisfy english_specification and the current generation_contract summary, memory, checklist, outputs, rules, englishsteps, and steps. Use generation_contract.steps as the formal step source when present; preserve its topology and resolve only defects required by workflow_schema or the matched Operation/Datatype contracts. Use only exact existing Operation IDs and typed ports from effective_operation_catalog and exact existing Datatype IDs from effective_datatype_catalog; retain explicit proposed markers for unresolved invented contracts. When a proposed LLM-backed Operation has a generation_contract.promptops entry, preserve that prompt binding as proposed provenance without claiming the prompt resource exists. Preserve stable IDs and valid unknown fields, bind every required input, make all loops finite, keep implementation selection for preflight or runtime, and conform to workflow_schema. Return one complete Workflow object inside the complete response envelope required by the calling authoring Operation, never a patch or independent step list."
  ))
)

(
  (kind prompt)
  (id workflow.generation.libops)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName libops)
  (classificationId english_to_workbench.20.operations.010.library)
  (produces ([] libops))
  (label "Select Library Operations From Current Workflow Information")
  (description "Select the relevant existing Operation prototypes from the effective library before requirement matching.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.libops from english_specification, the current generation_contract, existing_workflow, and effective_operation_catalog. Select only existing Operations plausibly relevant to the required workflow behaviors, values, branches, loops, side effects, and outputs. Preserve each selected Operation's exact operationId, label, description, typed inputs, and typed outputs from effective_operation_catalog. Do not rename Operations, invent ports, broaden semantics, include unrelated catalog entries, or decide final requirement matches in this stage. This is the grounded candidate library for the later matchops stage. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.matchops)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName matchops)
  (classificationId english_to_workbench.20.operations.020.match)
  (produces ([] matchops))
  (label "Match Operations From Current Workflow Information")
  (description "Match current Workflow requirements and steps to exact effective Operation prototypes and identify unresolved capabilities.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.matchops from english_specification, the current generation_contract, existing_workflow, generation_contract.libops, and effective_operation_catalog. For each required behavior or candidate workflow step, prefer the grounded libops shortlist and select an exact Operation ID only when its semantic purpose and typed input/output ports satisfy the requirement. Validate every chosen ID and port against effective_operation_catalog even when it appears in libops. Return entries with requirement, operationId, status, and rationale. status is matched or unresolved. For unresolved entries, leave operationId empty and state the missing semantic or port contract; never invent an Operation ID or port. Preserve stable valid matches unless current information invalidates them. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.inventops)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName inventops)
  (classificationId english_to_workbench.20.operations.030.invent)
  (produces ([] inventops))
  (label "Invent Operations From Current Workflow Information")
  (description "Propose complete semantic Operation contracts for unresolved Workflow capabilities without claiming they already exist.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.inventops from the unresolved entries in generation_contract.matchops, english_specification, existing_workflow, workflow_schema, and effective_operation_catalog. Invent one minimal proposed semantic Operation contract for each genuinely unresolved capability. Every proposal has requirement, operationId, description, inputs, outputs, constraints, and status. operationId must be a stable namespaced ID that does not collide with effective_operation_catalog. inputs and outputs must be complete typed port maps. constraints must state preconditions, postconditions, side effects, failure behavior, and finite bounds where relevant. status must be proposed. Reuse an existing Operation instead whenever its semantic and port contract already satisfies the requirement. These are proposals for later review and filesystem creation: do not claim they exist, do not select Python, Prolog, LLM, or other concrete implementations, and do not silently modify effective_operation_catalog. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.codeops)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName codeops)
  (classificationId english_to_workbench.20.operations.040.code)
  (produces ([] codeops))
  (label "Code Operations From Current Workflow Information")
  (description "Propose concrete implementations for reviewed invented Operation contracts without creating or applying source files.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.codeops from generation_contract.inventops, generation_contract.matchops, generation_contract.libops, english_specification, existing_workflow, workflow_schema, and effective_operation_catalog. For each reviewed invented Operation that still needs an implementation, propose one implementation contract with operationId, implementationId, implementationType, description, entrypoint, inputs, outputs, constraints, and status. Preserve the semantic Operation's exact typed ports. implementationType may be python, prolog, metta, llm, resource.tool, or composite only when justified by the contract; do not default every proposal to an LLM. entrypoint describes the proposed callable or resource path but must not claim that code or a file already exists. constraints must include validation, failure behavior, side effects, and finite bounds where relevant. status must be proposed. Reuse an existing implementation whenever effective_operation_catalog proves it satisfies the contract. This stage proposes implementation work only: do not write files, execute code, mutate the catalog, or mark proposals implemented. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.promptops)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName promptops)
  (classificationId english_to_workbench.20.operations.050.prompts)
  (produces ([] promptops))
  (label "Generate Prompts for New Operations From Current Workflow Information")
  (description "Propose prompt resources for newly invented LLM-backed Operations and bind them to their exact typed contracts.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.promptops from generation_contract.inventops, generation_contract.codeops, generation_contract.matchops, english_specification, existing_workflow, workflow_schema, effective_operation_catalog, and effective_prompt_catalog. Generate a prompt proposal only for a new Operation whose reviewed implementationType is llm or composite with an LLM stage. Do not generate prompts for deterministic python, prolog, metta, or resource.tool implementations unless their contract explicitly requires an LLM substage. Every proposal has operationId, promptId, label, instructions, inputBindings, outputContract, modelRequirements, and status. operationId must exactly reference a proposal in inventops/codeops. promptId must be stable, namespaced, non-colliding, and must not impersonate an existing prompt in effective_prompt_catalog. instructions must contain the complete reusable task instruction, required context, explicit exclusions, failure behavior, and a machine-checkable output contract without private chain-of-thought requests. inputBindings lists the exact Operation input port names. outputContract maps exact Operation output port names to their Datatypes. modelRequirements describe capabilities rather than a specific provider unless the Operation contract truly requires one. status must be proposed. Reuse an existing prompt only when effective_prompt_catalog proves that its task and bindings fit; otherwise retain a new proposal. Do not write files, mutate the prompt catalog, or claim proposals exist. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.libdt)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName libdt)
  (classificationId english_to_workbench.30.datatypes.010.library)
  (produces ([] libdt))
  (label "Select Library Datatypes From Current Workflow Information")
  (description "Select relevant existing semantic, representation, and concrete Datatype resources before requirement matching.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.libdt from english_specification, the current generation_contract, existing_workflow, effective_operation_catalog, and effective_datatype_catalog. Select only existing semantic_datatype, representation_datatype, and concrete_datatype resources plausibly required by workflow inputs, outputs, memory, artifacts, Operation ports, validation, serialization, or conversion. Preserve each selected resource's exact id as datatypeId, kind, label, description, parent relationships, constraints, and representation metadata from effective_datatype_catalog. Do not rename Datatypes, invent schemas, broaden semantics, include unrelated catalog entries, or decide final requirement matches in this stage. This is the grounded candidate library for matchdt. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.matchdt)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName matchdt)
  (classificationId english_to_workbench.30.datatypes.020.match)
  (produces ([] matchdt))
  (label "Match Datatypes From Current Workflow Information")
  (description "Match Workflow value and port requirements to exact effective Datatype resources and identify unresolved contracts.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.matchdt from english_specification, the current generation_contract, existing_workflow, generation_contract.libdt, effective_operation_catalog, and effective_datatype_catalog. For every workflow input, output, memory value, artifact, and Operation port requirement, prefer the grounded libdt shortlist and select exact datatypeId, representationId, and concreteDatatypeId values only when their declared contracts satisfy the requirement. Validate every selected ID and relationship against effective_datatype_catalog. Return entries with requirement, datatypeId, representationId, concreteDatatypeId, status, and rationale. status is matched or unresolved. For unresolved entries, leave unavailable IDs empty and describe the missing semantic, representation, validation, serialization, or conversion contract; never invent an ID in this stage. Preserve stable valid matches unless current information invalidates them. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.inventdt)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName inventdt)
  (classificationId english_to_workbench.30.datatypes.030.invent)
  (produces ([] inventdt))
  (label "Invent Datatypes From Current Workflow Information")
  (description "Propose missing semantic Datatype contracts without claiming the resources already exist.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.inventdt from unresolved generation_contract.matchdt entries, english_specification, existing_workflow, effective_operation_catalog, and effective_datatype_catalog. Invent one minimal semantic Datatype contract for each genuinely unresolved value meaning. Every proposal has requirement, datatypeId, kind, description, parents, constraints, and status. datatypeId must be stable, namespaced, and non-colliding; kind is semantic_datatype. constraints define meaning, admissible values, invariants, equality, and validation requirements without prematurely choosing an encoding. status must be proposed. Reuse an existing Datatype whenever its contract already fits. These are proposals for later review and filesystem creation: do not claim they exist, do not invent representation or concrete resources in this stage, and do not mutate effective_datatype_catalog. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.codedt)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName codedt)
  (classificationId english_to_workbench.30.datatypes.040.code)
  (produces ([] codedt))
  (label "Code Datatypes From Current Workflow Information")
  (description "Propose representation and concrete Datatype resources for reviewed invented semantic Datatypes without creating files.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.codedt from generation_contract.inventdt, generation_contract.matchdt, generation_contract.libdt, english_specification, existing_workflow, effective_operation_catalog, and effective_datatype_catalog. For each reviewed invented semantic Datatype that needs an executable representation, propose a representation contract with datatypeId, representationId, concreteDatatypeId, encoding, validator, conversionOperations, constraints, and status. Preserve the semantic meaning and reference only exact existing conversion Operation IDs when available. representationId and concreteDatatypeId must be stable, namespaced, and non-colliding. validator describes a proposed callable or declarative schema but must not claim that code exists. status must be proposed. Reuse existing representation and concrete Datatype resources whenever they satisfy the contract. This stage proposes implementation resources only: do not write files, run validators, mutate catalogs, or mark proposals implemented. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.englishsteps)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName englishsteps)
  (classificationId english_to_workbench.10.contract.060.englishsteps)
  (produces ([] englishsteps))
  (label "Generate English Steps From Current Workflow Information")
  (description "Describe the intended Workflow as an ordered, readable control-flow outline before binding formal Operations and Datatypes.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.englishsteps from english_specification, the current generation_contract, and existing_workflow. Return an ordered array of objects with stepId, label, purpose, dependsOn, and controlFlow. Explain every required action, branch, loop, retry, termination path, side effect, memory interaction, and output in plain English. Use stable stepId values so later stages can refer to them. dependsOn contains prior English step IDs. controlFlow concisely identifies sequence, branch, while, for-each, call, return, or another explicit structure. Do not choose Operation IDs, Datatype IDs, implementations, code, or file paths in this stage. Preserve ambiguity as explicit alternatives or unresolved notes rather than silently deciding it. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.steps)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName steps)
  (classificationId english_to_workbench.10.contract.070.steps)
  (produces ([] steps))
  (label "Generate Formal Steps From Current Workflow Information")
  (description "Translate the English step outline into formal Workflow step objects grounded in matched Operations and Datatypes.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.steps from generation_contract.englishsteps, generation_contract.matchops, generation_contract.inventops, generation_contract.matchdt, generation_contract.inventdt, the current generation_contract, existing_workflow, effective_operation_catalog, effective_datatype_catalog, and workflow_schema. Return an ordered array of complete formal Workflow step objects. Each step must satisfy workflow_schema and include stable id, label, kind, operation, dependsOn, inputs, and outputs, plus explicit parameters, branch, while, foreach, or maximum bounds when required. Use exact existing Operation and Datatype IDs when matched. A proposed ID from inventops or inventdt may be referenced only with an explicit proposed/unresolved marker. Preserve the English step topology, including loop reevaluation, branches, calls, and termination. Do not wrap these steps in a second Workflow object; the workflow stage performs final assembly. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.libwf)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName libwf)
  (classificationId english_to_workbench.40.workflows.010.library)
  (produces ([] libwf))
  (label "Select Library Workflows From Current Workflow Information")
  (description "Select relevant existing Workflow resources that may be reused or revised before Workflow matching.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.libwf from english_specification, the current generation_contract, existing_workflow, and effective_workflow_catalog. Select only existing Workflows plausibly reusable as the target, a referenced subworkflow, or a structural precedent. Preserve exact workflowId, label, description, typed inputs, and typed outputs from effective_workflow_catalog. Do not rename Workflows, invent steps, copy unrelated resources, or decide final matches in this stage. This is the grounded candidate library for matchwf. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.matchwf)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName matchwf)
  (classificationId english_to_workbench.40.workflows.020.match)
  (produces ([] matchwf))
  (label "Match Workflows From Current Workflow Information")
  (description "Match requested behavior to existing Workflow resources and identify what still requires a new or revised Workflow.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.matchwf from english_specification, generation_contract.englishsteps, generation_contract.libwf, the current generation_contract, existing_workflow, and effective_workflow_catalog. For each complete Workflow-level requirement, select an exact workflowId only when its purpose, typed interface, and control-flow contract fit. Return entries with requirement, workflowId, status, and rationale. status is matched or unresolved. For unresolved entries, leave workflowId empty and explain the missing or required revision; never invent a Workflow ID in this stage. Treat the current existing_workflow as a revisable match when appropriate. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.inventwf)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName inventwf)
  (classificationId english_to_workbench.40.workflows.030.invent)
  (produces ([] inventwf))
  (label "Invent Workflows From Current Workflow Information")
  (description "Propose missing Workflow contracts without claiming that new Workflow resources already exist.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise generation_contract.inventwf from unresolved generation_contract.matchwf entries, generation_contract.englishsteps, english_specification, existing_workflow, and effective_workflow_catalog. Invent one minimal Workflow contract for each genuinely unresolved Workflow-level capability. Every proposal has requirement, workflowId, description, typed inputs, typed outputs, constraints, and status. workflowId must be stable, namespaced, and non-colliding. constraints cover entry, success, failure, side effects, termination, and bounded loops. status must be proposed. Prefer revising existing_workflow or reusing an effective Workflow when it fits. These are proposals only: do not claim resources or steps exist and do not mutate the catalog. Return the complete response envelope required by the calling authoring Operation."
  ))
)

(
  (kind prompt)
  (id workflow.generation.codewf)
  (applicability ([] english_to_workbench.contract_section))
  (buttonName codewf)
  (classificationId english_to_workbench.40.workflows.040.code)
  (produces ([] codewf))
  (label "Code Workflow From Current Workflow Information")
  (description "Assemble the single candidate Workflow from formal steps and record an auditable build report.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Produce or revise the top-level workflow candidate and generation_contract.codewf from generation_contract.steps, generation_contract.matchwf, generation_contract.inventwf, generation_contract.matchops, generation_contract.inventops, generation_contract.codeops, generation_contract.promptops, generation_contract.matchdt, generation_contract.inventdt, generation_contract.codedt, english_specification, existing_workflow, workflow_schema, effective_workflow_catalog, effective_operation_catalog, effective_datatype_catalog, and effective_prompt_catalog. Revise existing_workflow as the one candidate Workflow; never return a second competing Workflow object. Preserve stable IDs where semantics remain valid, install the formal steps in dependency-valid order, retain explicit bounded branches and loops, and preserve proposed prompt bindings for LLM-backed Operation implementations. codewf is an array containing a build report with workflowId, stepIds, operationIds, datatypeIds, unresolvedOperations, unresolvedDatatypes, and status. status is proposed, complete, or unresolved. Do not write the Workflow to disk or claim proposed Operations, prompts, or Datatypes are implemented. Return the complete response envelope required by the calling authoring Operation."
  ))
)
