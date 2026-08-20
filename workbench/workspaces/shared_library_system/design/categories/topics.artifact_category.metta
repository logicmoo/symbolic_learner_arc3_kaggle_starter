(
  (kind artifact_category)
  (id topics.agent_interaction)
  (label "Agent Interaction")
  (description "Multi-agent interaction: capture exchanges, compose responses, reason about requests, retain interactions.")
  (path agent-interaction)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains agent-interaction)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.arc3)
  (label "Arc3")
  (description "Operations specific to the ARC-AGI-3 game-playing pipeline.")
  (path arc3)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains arc3)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.artifacts)
  (label "Artifacts")
  (description "Audit and bundle produced artifacts.")
  (path artifacts)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains artifacts)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.atomspaces)
  (label "Atomspaces")
  (description "Query and mutate AtomSpaces (assert, retract, inspect).")
  (path atomspaces)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains atomspaces)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.collection_building)
  (label "Collection Building")
  (description "Build or sample from collections.")
  (path collection-building)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains collection-building)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.conditional_branching)
  (label "Conditional Branching")
  (description "Select a branch in conditional control flow.")
  (path conditional-branching)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains conditional-branching)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.conditionals)
  (label "Conditionals")
  (description "Evaluate conditions and choose branches.")
  (path conditionals)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains conditionals)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.control_flow)
  (label "Control Flow")
  (description "Workflow control-flow constructs: conditionals, loops, and branches.")
  (path control-flow)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains control-flow)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.core_primitives)
  (label "Core Primitives")
  (description "Core primitive operations: echo, constant, select, and resource validation.")
  (path core-primitives)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains core-primitives)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.data_merge_select)
  (label "Data Merge Select")
  (description "Record-level data transformation: merge records and select fields.")
  (path data-merge-select)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains data-merge-select)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.datatypes)
  (label "Datatypes")
  (description "Datatype representation and conversion between bitmaps, objects, and scene graphs.")
  (path datatypes)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains datatypes)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.gallery_inspection)
  (label "Gallery Inspection")
  (description "Assemble gallery / inspection views of upstream artifacts.")
  (path gallery-inspection)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains gallery-inspection)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.games)
  (label "Games")
  (description "Game selection and play-loop control for the ARC game player.")
  (path games)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains games)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.goals)
  (label "Goals")
  (description "Interpret, evaluate, and check satisfaction of goals.")
  (path goals)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains goals)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.graphics)
  (label "Graphics")
  (description "Turtle/LOGO rendering and reconstruction of programs from objects or scene graphs.")
  (path graphics)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains graphics)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.knowledge_inspection)
  (label "Knowledge Inspection")
  (description "Inspect data and artifact knowledge.")
  (path knowledge-inspection)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains knowledge-inspection)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.learning)
  (label "Learning")
  (description "Learn from evidence: apply/grade rules, form hypotheses, and update the world model.")
  (path learning)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains learning)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.loops)
  (label "Loops")
  (description "Loop control: while, continue, and break.")
  (path loops)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains loops)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.model_control)
  (label "Model Control")
  (description "Compare and control model runs and grounding.")
  (path model-control)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains model-control)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.object_identity)
  (label "Object Identity")
  (description "Assign and maintain stable identities for entities across views, states, or time.")
  (path object-identity)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains object-identity)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.observation)
  (label "Observation")
  (description "Capture observations of a world's current state.")
  (path observation)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains observation)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.operation_invocation)
  (label "Operation Invocation")
  (description "Invoke an existing operation from a conditional branch.")
  (path operation-invocation)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains operation-invocation)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.planning)
  (label "Planning")
  (description "Generate and validate planning strategies and planned workflows.")
  (path planning)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains planning)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.policies)
  (label "Policies")
  (description "Evaluate and explain policy decisions.")
  (path policies)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains policies)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.programming_control_flow)
  (label "Programming Control Flow")
  (description "Programming control flow: return from a call or frame.")
  (path programming-control-flow)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains programming-control-flow)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.prompts)
  (label "Prompts")
  (description "Render and compose prompt resources.")
  (path prompts)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains prompts)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.recognition_memory)
  (label "Recognition Memory")
  (description "Recognition memory: capture, normalize, establish, and publish durable memory records.")
  (path recognition-memory)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains recognition-memory)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.resource_tools)
  (label "Resource Tools")
  (description "Resource-tool operations that inspect or act on filesystem resources (cross-cutting).")
  (path resource-tools)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains resource-tools)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.sample_demos)
  (label "Sample Demos")
  (description "Sample / demonstration operations and their concrete implementations.")
  (path sample-demos)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains sample-demos)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.segmentation)
  (label "Segmentation")
  (description "Partition an observation into candidate entities or connected components; independent of whether the input is visual.")
  (path segmentation)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains segmentation)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.symbolic)
  (label "Symbolic")
  (description "Symbolic reasoning: rule induction, explanation, validation, and Prolog evidence.")
  (path symbolic)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains symbolic)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems)
  (label "Systems")
  (description "Umbrella for operations backed by, or that inspect, a system runtime.")
  (path systems)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems_inspection)
  (label "Systems Inspection")
  (description "Inspect external or target systems for state and readiness.")
  (path systems/systems-inspection)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems-inspection)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems_llm)
  (label "Systems Llm")
  (description "Backed by an LLM completion runtime.")
  (path systems/systems-llm)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems-llm)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems_prolog)
  (label "Systems Prolog")
  (description "Backed by a Prolog runtime (source or query).")
  (path systems/systems-prolog)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems-prolog)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems_python)
  (label "Systems Python")
  (description "Backed by a Python callable/expression runtime.")
  (path systems/systems-python)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems-python)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.systems_workbench)
  (label "Systems Workbench")
  (description "Backed by the workbench system runtime (e.g. requesting input from the user).")
  (path systems/systems-workbench)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains systems-workbench)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.taxonomy)
  (label "Taxonomy")
  (description "Inspect or resolve the artifact-category / topic taxonomy.")
  (path taxonomy)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains taxonomy)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.text)
  (label "Text")
  (description "Text transformation and understanding.")
  (path text)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains text)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.vision)
  (label "Vision")
  (description "Visual perception: reason over images or visual states. Separate from segmentation.")
  (path vision)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains vision)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.workflow)
  (label "Workflow")
  (description "Umbrella for authoring workflows and the workflow-language primitives that compose them.")
  (path workflow)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains workflow)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.workflow_authoring)
  (label "Workflow Authoring")
  (description "Generate or analyze workflows from English specifications and generation contracts.")
  (path workflow/workflow-authoring)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains workflow-authoring)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.workflow_language)
  (label "Workflow Language")
  (description "The workflow-language primitives (loops, conditionals, values, memory, return) that compose workflows; scopes the operation catalog during workflow generation.")
  (path workflow/workflow-language)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains workflow-language)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.workflow_values)
  (label "Workflow Values")
  (description "Read, set, and compare workflow values.")
  (path workflow/workflow-values)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains workflow-values)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.world_modeling)
  (label "World Modeling")
  (description "Build or revise a world model: entities, transitions, hypotheses, and evidence.")
  (path world-modeling)
  (trees ([]
    operations
  ))
  (query (
    (kinds ([]
      operation
    ))
    (where (
      (topics (
        (contains world-modeling)
      ))
    ))
  ))
  (parentMode show)
)
