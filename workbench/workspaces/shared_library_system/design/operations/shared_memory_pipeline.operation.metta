(
  (kind operation)
  (id shared.capture_learning_examples)
  (label "Capture Learning Examples")
  (description "Capture a batch of examples without discarding source ordering or provenance.")
  (topics ([]
    learning
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value VisualExampleSet)))
  (outputs ((value VisualExampleSet)))
  (parameters ())
)
(
  (kind operation)
  (id shared.normalize_learning_evidence)
  (label "Normalize Learning Evidence")
  (description "Stage evidence in a stable form before review or memory publication.")
  (topics ([]
    learning
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value Any)))
  (parameters ())
)
(
  (kind operation)
  (id shared.establish_recognizable_memory)
  (label "Establish Recognizable Memory")
  (description "Promote perceived evidence into a recognizable memory candidate while retaining provenance.")
  (topics ([]
    vision
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value RecognizableMemory)))
  (parameters ())
)
(
  (kind operation)
  (id shared.publish_memory_record)
  (label "Publish Memory Record")
  (description "Combine staged evidence with review or context into a durable memory record.")
  (topics ([]
    recognition-memory
    learning
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value RecognizableMemory)))
  (parameters ())
)
(
  (kind operation)
  (id shared.bind_memory_context)
  (label "Bind Memory Context")
  (description "Bind a recognizable memory to its domain or runtime context.")
  (topics ([]
    recognition-memory
    world-modeling
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value ContextualMemory)))
  (parameters ())
)
(
  (kind operation)
  (id shared.capture_agent_exchange)
  (label "Capture Agent Exchange")
  (description "Capture one agent observation, request, or message as stable evidence.")
  (topics ([]
    agent-interaction
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value AgentExchange)))
  (parameters ())
)
(
  (kind operation)
  (id shared.stage_microatoms)
  (label "Stage Micro-Atoms")
  (description "Stage the smallest meaningful facts extracted from an agent exchange.")
  (topics ([]
    atomspaces
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value AgentExchange)))
  (outputs ((value MicroAtomSet)))
  (parameters ())
)
(
  (kind operation)
  (id shared.compose_agent_response)
  (label "Compose Agent Response Record")
  (description "Bind a request to a proposed response for inspection and retention.")
  (topics ([]
    agent-interaction
    recognition-memory
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value AgentExchange)))
  (parameters ())
)
(
  (kind operation)
  (id shared.retain_agent_interaction)
  (label "Retain Agent Interaction")
  (description "Combine observed context and response evidence into retained interaction memory.")
  (topics ([]
    agent-interaction
    recognition-memory
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value AgentInteractionMemory)))
  (parameters ())
)
(
  (kind operation)
  (id shared.reason_about_request)
  (label "Reason About Request")
  (description "Produce an inspectable reasoning trace from a request before symbolic translation.")
  (topics ([]
    agent-interaction
    symbolic
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value LlmReasoningTrace)))
  (parameters ())
)
(
  (kind operation)
  (id shared.generate_atomese)
  (label "Generate Atomese Candidate")
  (description "Translate a reasoning trace into an Atomese program candidate.")
  (topics ([]
    atomspaces
    symbolic
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value AtomeseProgram)))
  (parameters ())
)
(
  (kind operation)
  (id shared.assess_symbolic_coverage)
  (label "Assess Symbolic Coverage")
  (description "Validate an Atomese candidate and report whether its symbolic coverage is adequate.")
  (topics ([]
    atomspaces
    symbolic
    systems-python
  ))
  (implementation python.expression)
  (inputs ((context Object)))
  (outputs ((value SymbolicCoverageAssessment)))
  (parameters ())
)
(
  (kind operation)
  (id shared.repair_atomese)
  (label "Repair Atomese Candidate")
  (description "Apply one bounded repair candidate in a symbolic coverage retry sequence.")
  (topics ([]
    atomspaces
    symbolic
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value AtomeseProgram)))
  (parameters ())
)
(
  (kind operation)
  (id shared.execute_symbolic_report)
  (label "Execute and Report Symbolic Result")
  (description "Bind adequate Atomese and its coverage assessment into an execution report.")
  (topics ([]
    atomspaces
    symbolic
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value SymbolicExecutionReport)))
  (parameters ())
)
(
  (kind operation)
  (id shared.run_weaker_model_control)
  (label "Run Weaker-Model Control")
  (description "Capture a weaker-model rerun of the same task as a control after memory is judged sufficient.")
  (topics ([]
    model-control
    recognition-memory
    core-primitives
  ))
  (implementation core.echo)
  (inputs ((value Any)))
  (outputs ((value WeakerModelControl)))
  (parameters ())
)
(
  (kind operation)
  (id shared.compare_memory_grounding)
  (label "Compare Memory Grounding")
  (description "Bind the memory-grounded symbolic result to a weaker-model control for attribution evidence.")
  (topics ([]
    model-control
    recognition-memory
    core-primitives
  ))
  (implementation core.merge)
  (inputs ((left Any) (right Any)))
  (outputs ((value MemoryGroundingEvidence)))
  (parameters ())
)
