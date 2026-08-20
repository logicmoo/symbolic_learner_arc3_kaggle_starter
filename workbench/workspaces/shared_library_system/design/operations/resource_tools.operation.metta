(
  (kind operation)
  (id resource_validate)
  (label "Validate Resource")
  (description "Validate the common identity and enablement contract of any filesystem resource.")
  (topics ([]
    core-primitives
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource Resource)))
  (outputs ((result ResourceValidation)))
  (parameters ((action resource.validate)))
)
(
  (kind operation)
  (id datatype_sample)
  (label "Generate Datatype Sample")
  (description "Generate a representative sample and list the declared representation relationships for a datatype resource.")
  (topics ([]
    datatypes
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource DatatypeContract)))
  (outputs ((result DatatypeSample)))
  (parameters ((action datatype.sample)))
)
(
  (kind operation)
  (id prompt_render)
  (label "Render Prompt Resource")
  (description "Render and inspect the selected prompt or prompt implementation before model invocation.")
  (topics ([]
    prompts
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource PromptResource)))
  (outputs ((result Text)))
  (parameters ((action prompt.render)))
)
(
  (kind operation)
  (id goal_evaluate)
  (label "Evaluate Goal")
  (description "Evaluate a Goal's declared success criteria against the currently supplied evidence.")
  (topics ([]
    goals
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource Goal)))
  (outputs ((result Evaluation)))
  (parameters ((action goal.evaluate)))
)
(
  (kind operation)
  (id planning_strategy_preview)
  (label "Preview Planning Strategy")
  (description "Inspect how a Planning Strategy proposes or selects a Planned Workflow.")
  (topics ([]
    planning
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource PlanningStrategy)))
  (outputs ((result PlannedWorkflow)))
  (parameters ((action planning.preview)))
)
(
  (kind operation)
  (id atomspace_inspect)
  (label "Inspect AtomSpace")
  (description "Inspect AtomSpace bindings and the event semantics produced when its Atoms change.")
  (topics ([]
    atomspaces
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource AtomSpace)))
  (outputs ((result AtomSpaceQueryResult)))
  (parameters ((action atomspace.inspect)))
)
(
  (kind operation)
  (id policy_evaluate)
  (label "Evaluate Policy")
  (description "Resolve and explain the effective enabled state and declared rules of a Policy resource.")
  (topics ([]
    policies
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource Policy)))
  (outputs ((result PolicyDecision)))
  (parameters ((action policy.evaluate)))
)
(
  (kind operation)
  (id category_preview)
  (label "Preview Category Query")
  (description "Inspect a first-class Category query, target trees, path, and parent display behavior.")
  (topics ([]
    taxonomy
    resource-tools
  ))
  (implementation resource.tool)
  (inputs ((resource ArtifactCategory)))
  (outputs ((result CategoryMatchSet)))
  (parameters ((action category.preview)))
)
(
  (kind operation) (id datatype_validate) (label "Validate Datatype Contract")
  (description "Validate a datatype and its semantic, representation, or concrete relationships.")
  (topics ([]
    datatypes
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource DatatypeContract))) (outputs ((result ResourceValidation))) (parameters ((action datatype.validate)))
)
(
  (kind operation) (id datatype_conversion_inspect) (label "Inspect Datatype Conversions")
  (description "Inspect declared or implied conversion relationships for a datatype resource.")
  (topics ([]
    datatypes
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource DatatypeContract))) (outputs ((result ConversionInventory))) (parameters ((action datatype.conversions)))
)
(
  (kind operation) (id prompt_compose) (label "Compose Prompt Resource")
  (description "Resolve the ordered prompt members and separator contributed by a prompt profile.")
  (topics ([]
    prompts
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource PromptResource))) (outputs ((result PromptComposition))) (parameters ((action prompt.compose)))
)
(
  (kind operation) (id goal_interpret) (label "Interpret Goal")
  (description "Inspect the available interpretations, preferred interpretation, and success criteria of a Goal.")
  (topics ([]
    goals
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource Goal))) (outputs ((result GoalInterpretation))) (parameters ((action goal.interpret)))
)
(
  (kind operation) (id goal_check_satisfaction) (label "Check Goal Satisfaction")
  (description "Count satisfied and unknown Goal success criteria against available evidence.")
  (topics ([]
    goals
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource Goal))) (outputs ((result GoalSatisfaction))) (parameters ((action goal.satisfaction)))
)
(
  (kind operation) (id planning_strategy_generate) (label "Generate Planned Workflow")
  (description "Prepare a Planning Strategy and its goals for production of a Planned Workflow.")
  (topics ([]
    planning
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource PlanningStrategy))) (outputs ((result PlannedWorkflow))) (parameters ((action planning.generate)))
)
(
  (kind operation) (id planned_workflow_validate) (label "Validate Planned Workflow")
  (description "Validate whether a Planning Strategy identifies enough information to produce or select a Workflow.")
  (topics ([]
    planning
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource PlannedWorkflow))) (outputs ((result ResourceValidation))) (parameters ((action planning.validate)))
)
(
  (kind operation) (id atomspace_query) (label "Query AtomSpace")
  (description "Run a read-only query against the selected AtomSpace contract and inspect matches.")
  (topics ([]
    atomspaces
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource AtomSpace))) (outputs ((result AtomSpaceQueryResult))) (parameters ((action atomspace.query)))
)
(
  (kind operation) (id atomspace_assert) (label "Assert Atoms")
  (description "Prepare Atoms to assert into an AtomSpace and describe the resulting change Event.")
  (topics ([]
    atomspaces
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource AtomSpace))) (outputs ((result AtomSpaceChange))) (parameters ((action atomspace.assert)))
)
(
  (kind operation) (id atomspace_retract) (label "Retract Atoms")
  (description "Prepare Atoms to retract from an AtomSpace and describe the resulting change Event.")
  (topics ([]
    atomspaces
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource AtomSpace))) (outputs ((result AtomSpaceChange))) (parameters ((action atomspace.retract)))
)
(
  (kind operation) (id system_inspect) (label "Inspect System")
  (description "Inspect a callable System's type, provider, capabilities, enablement, and non-secret configuration shape.")
  (topics ([]
    systems-inspection
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource SystemContract))) (outputs ((result SystemInspection))) (parameters ((action system.inspect)))
)
(
  (kind operation) (id system_check_readiness) (label "Check System Readiness")
  (description "Check whether a System is enabled and declares the provider and capabilities required for execution without launching it.")
  (topics ([]
    systems-inspection
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource SystemContract))) (outputs ((result SystemReadiness))) (parameters ((action system.check_readiness)))
)
(
  (kind operation) (id data_inspect) (label "Inspect Data Value")
  (description "Inspect the type, media format, size, provider path, and loaded-value state of selected workspace Data.")
  (topics ([]
    knowledge-inspection
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource DataValue))) (outputs ((result DataInspection))) (parameters ((action data.inspect)))
)
(
  (kind operation) (id artifact_inspect) (label "Inspect Persisted Artifact")
  (description "Inspect the type, media format, size, storage lifecycle, and loaded-value state of a persisted Artifact.")
  (topics ([]
    knowledge-inspection
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource Artifact))) (outputs ((result ArtifactInspection))) (parameters ((action artifact.inspect)))
)
(
  (kind operation) (id policy_explain) (label "Explain Policy Decision")
  (description "Explain the inheritance and decision inputs behind a Policy's effective state.")
  (topics ([]
    policies
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource Policy))) (outputs ((result PolicyDecision))) (parameters ((action policy.explain)))
)
(
  (kind operation) (id category_resolve_matches) (label "Resolve Category Matches")
  (description "Resolve and inspect the resources selected by a first-class Category query.")
  (topics ([]
    taxonomy
    resource-tools
  )) (implementation resource.tool)
  (inputs ((resource ArtifactCategory))) (outputs ((result CategoryMatchSet))) (parameters ((action category.matches)))
)
