(
  (kind artifact_category)
  (id topics.cap.vision)
  (label "Vision")
  (description "Models, systems, and prompts that declare a visual (image) capability.")
  (path vision)
  (trees ([]
    models
    prompts
  ))
  (query (
    (kinds ([]
      backend
      model
      system
      prompt
      prompt_implementation
      prompt_profile
    ))
    (where (
      (capabilities (
        (contains vision)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.vision_llm)
  (label "Vision")
  (description "Models and prompts declaring the llm.vision capability.")
  (path vision)
  (trees ([]
    models
    prompts
  ))
  (query (
    (kinds ([]
      backend
      model
      system
      prompt
      prompt_implementation
      prompt_profile
    ))
    (where (
      (capabilities (
        (contains llm.vision)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.reasoning)
  (label "Reasoning")
  (description "Models, systems, and prompts that declare a reasoning capability.")
  (path reasoning)
  (trees ([]
    models
    prompts
  ))
  (query (
    (kinds ([]
      backend
      model
      system
      prompt
      prompt_implementation
      prompt_profile
    ))
    (where (
      (capabilities (
        (contains reasoning)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.reasoning_llm)
  (label "Reasoning")
  (description "Models and prompts declaring the llm.reasoning capability.")
  (path reasoning)
  (trees ([]
    models
    prompts
  ))
  (query (
    (kinds ([]
      backend
      model
      system
      prompt
      prompt_implementation
      prompt_profile
    ))
    (where (
      (capabilities (
        (contains llm.reasoning)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.systems_llm)
  (label "Systems Llm")
  (description "Resources with the llm.complete capability (LLM caller runtime).")
  (path systems/systems-llm)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains llm.complete)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.systems_prolog)
  (label "Systems Prolog")
  (description "Resources with the prolog.query capability.")
  (path systems/systems-prolog)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains prolog.query)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.systems_python_callable)
  (label "Systems Python")
  (description "Resources with the python.callable capability.")
  (path systems/systems-python)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains python.callable)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.systems_python_expression)
  (label "Systems Python")
  (description "Resources with the python.expression capability.")
  (path systems/systems-python)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains python.expression)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.systems_metta)
  (label "Systems Metta")
  (description "Resources with the metta.evaluate capability.")
  (path systems/systems-metta)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains metta.evaluate)
      ))
    ))
  ))
  (parentMode show)
)

(
  (kind artifact_category)
  (id topics.cap.agent_interaction)
  (label "Agent Interaction")
  (description "Systems that can invoke or message agents.")
  (path agent-interaction)
  (trees ([]
    models
  ))
  (query (
    (kinds ([]
      backend
      model
      system
    ))
    (where (
      (capabilities (
        (contains agent.invoke)
      ))
    ))
  ))
  (parentMode show)
)
