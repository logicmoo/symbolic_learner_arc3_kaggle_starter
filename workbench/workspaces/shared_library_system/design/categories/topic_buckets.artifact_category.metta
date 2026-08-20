(
  (kind artifact_category)
  (id topics.bucket.datatypes)
  (label "Datatypes")
  (description "All datatype resources (semantic, representation, concrete). Auto-bucketed by kind for UI selection.")
  (path datatypes)
  (trees ([]
    datatypes
  ))
  (query (
    (kinds ([]
      semantic_datatype
      representation_datatype
      concrete_datatype
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.prompts)
  (label "Prompts")
  (description "All prompt resources (prompts, implementations, profiles). Auto-bucketed by kind for UI selection.")
  (path prompts)
  (trees ([]
    prompts
  ))
  (query (
    (kinds ([]
      prompt
      prompt_implementation
      prompt_profile
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.models)
  (label "Models")
  (description "All model and backend resources. Auto-bucketed by kind for UI selection.")
  (path models)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.systems)
  (label "Systems")
  (description "All callable system resources. Auto-bucketed by kind for UI selection.")
  (path systems)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      system
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.systems_python)
  (label "Systems Python")
  (description "System resources backed by the Python runtime.")
  (path systems/systems-python)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      system
    ))
    (where (
      (provider (
        (equals python)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.systems_prolog)
  (label "Systems Prolog")
  (description "System resources backed by the Prolog runtime.")
  (path systems/systems-prolog)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      system
    ))
    (where (
      (provider (
        (equals prolog)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.systems_metta)
  (label "Systems Metta")
  (description "System resources backed by the MeTTa runtime.")
  (path systems/systems-metta)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      system
    ))
    (where (
      (provider (
        (equals metta)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.bucket.systems_llm)
  (label "Systems Llm")
  (description "System resources backed by the LLM caller runtime.")
  (path systems/systems-llm)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      system
    ))
    (where (
      (provider (
        (equals llm)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.todo_needs_categorization)
  (label "Todo Needs Categorization")
  (description "Resources that have not yet been given explicit topics. Auto-collected by kind so a human (or the topic editor) can categorize them.")
  (path todo-needs-categorization)
  (trees ([]
    datatypes
    prompts
    models
  ))
  (query (
    (kinds ([]
      semantic_datatype
      representation_datatype
      concrete_datatype
      prompt
      prompt_implementation
      prompt_profile
      backend
      model
      system
    ))
  ))
  (parentMode show)
)
