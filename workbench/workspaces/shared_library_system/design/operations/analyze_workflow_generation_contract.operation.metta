(
  (kind operation)
  (id workflow.analyze_generation_contract)
  (label "Analyze Workflow Generation Contract")
  (description "Generate a complete English-to-Workflow contract in one LLM call, honoring an experimental section order so ordering effects can be compared.")
  (topics ([]
    workflow-authoring
    planning
  ))
  (inputs (
    (english_specification Text)
    (generation_steps Array)
    (existing_generation_contract Object)
    (existing_workflow Object)
    (existing_memory_values_plan Object)
    (effective_operation_catalog Array)
    (effective_datatype_catalog Array)
    (effective_workflow_catalog Array)
    (effective_prompt_catalog Array)
    (workflow_schema Object)
  ))
  (outputs (
    (generation_contract Object)
    (workflow Object)
    (order_used Array)
  ))
  (specializations (
    (workflow.analyze_generation_contract.json (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization workflow.analyze_generation_contract.json)
)
(
  (kind operation)
  (id workflow.analyze_generation_contract.json)
  (label "Analyze Workflow Generation Contract / JSON")
  (topics ([]
    workflow-authoring
    systems-llm
  ))
  (implementation llm.complete)
  (implements (
    (workflow.analyze_generation_contract (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (inputs (
    (english_specification Text)
    (generation_steps Array)
    (existing_generation_contract Object)
    (existing_workflow Object)
    (existing_memory_values_plan Object)
    (effective_operation_catalog Array)
    (effective_datatype_catalog Array)
    (effective_workflow_catalog Array)
    (effective_prompt_catalog Array)
    (workflow_schema Object)
  ))
  (outputs (
    (generation_contract Object)
    (workflow Object)
    (order_used Array)
  ))
  (bindings (
    (prompts ([]
      workflow.analyze_generation_contract
    ))
    (promptVariants (
      (workflow.analyze_generation_contract workflow.analyze_generation_contract.json)
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy policy)
  ))
  (parameters (
    (parseJson true)
    (responseFormat json_object)
  ))
)
