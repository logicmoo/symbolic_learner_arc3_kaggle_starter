(
  (kind backend)
  (id https.inference.asicloud.cudos.org.v1)
  (aliases ([]
    asicloud
    asi-cloud
    cudos
    https://inference.asicloud.cudos.org/v1
  ))
  (label ASICloud)
  (provider asicloud)
  (official true)
  (description "ASI Alliance OpenAI-compatible inference transport hosted by ASICloud on CUDOS, including the asi1-mini route.")
  (enabled false)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.tools
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl https://inference.asicloud.cudos.org/v1)
    (apiKeyEnvironmentVariable ASI_API_KEY)
    (defaultModel asi1-mini)
    (baseUrlEnvironmentVariable WORKBENCH_ASICLOUD_BASE_URL)
    (modelEnvironmentVariable WORKBENCH_ASICLOUD_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 900)
  ))
  (categories ([]
    backends
    models
    reasoning
    systems/systems-llm
    todo-needs-categorization
  ))
  (dependedOnBy (
    (asicloud-asi1 ())
    (https.inference.asicloud.cudos.org.v1-model ())
    (asicloud-asi1-mini ())
  ))
  (implementedBy (
    (asicloud-asi1 ())
    (asicloud-asi1-mini ())
    (https.inference.asicloud.cudos.org.v1-model ())
  ))
  (inheritedBy (
    (asicloud-asi1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (asicloud-asi1-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (https.inference.asicloud.cudos.org.v1-model (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
  ))
)
