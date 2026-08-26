(
  (kind semantic_datatype)
  (id visual_example_set)
  (label "Visual Example Set")
  (description "An ordered collection of visual examples with source and learning provenance.")
  (specializations ())
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id recognizable_memory)
  (label "Recognizable Memory")
  (description "Evidence promoted into a stable, reviewable memory that can be recognized again.")
  (specializations (
    (contextual_memory (
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
    (agent_interaction_memory (
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
    (symbolic_execution_report (
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
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id contextual_memory)
  (label "Contextual Memory")
  (description "A recognizable memory bound to domain, task, or runtime context.")
  (specializations ())
  (implements (
    (recognizable_memory (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id agent_exchange)
  (label "Agent Exchange")
  (description "One provenance-bearing observation, request, message, or response exchanged by agents.")
  (specializations (
    (microatom_set (
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
    (agent_interaction_memory (
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
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id microatom_set)
  (label "Micro-Atom Set")
  (description "A reviewable set of minimal facts derived from an agent exchange.")
  (specializations ())
  (implements (
    (agent_exchange (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id agent_interaction_memory)
  (label "Agent Interaction Memory")
  (description "Retained conversational context, request, response, and provenance for an agent interaction.")
  (specializations ())
  (implements (
    (recognizable_memory (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (agent_exchange (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id llm_reasoning_trace)
  (label "LLM Reasoning Trace")
  (description "An inspectable reasoning artifact produced before symbolic translation.")
  (specializations (
    (atomese_program (
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
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id atomese_program)
  (label "Atomese Program")
  (description "A generated or repaired symbolic program ready for validation and execution.")
  (specializations ())
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (llm_reasoning_trace (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id symbolic_coverage_assessment)
  (label "Symbolic Coverage Assessment")
  (description "Validation evidence and an adequacy decision for a symbolic program candidate.")
  (specializations (
    (memory_grounding_evidence (
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
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id symbolic_execution_report)
  (label "Symbolic Execution Report")
  (description "The adequate symbolic candidate, its validation evidence, and execution result.")
  (specializations ())
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (recognizable_memory (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id weaker_model_control)
  (label "Weaker-Model Control")
  (description "A same-task result from a deliberately weaker model used to control for model priors.")
  (specializations (
    (memory_grounding_evidence (
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
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind semantic_datatype)
  (id memory_grounding_evidence)
  (label "Memory-Grounding Evidence")
  (description "Comparison evidence attributing symbolic performance to stored memory rather than model strength alone.")
  (specializations ())
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (symbolic_coverage_assessment (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
    (weaker_model_control (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
