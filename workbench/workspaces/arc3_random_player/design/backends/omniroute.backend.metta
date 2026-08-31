(
  (kind backend)
  (id omniroute)
  (label OmniRoute)
  (provider omniroute)
  (official true)
  (description "Local OmniRoute OpenAI-compatible gateway. run_workbench.bat starts it on port 20128 and provisions its endpoint key into the inherited workspace credential store.")
  (enabled false)
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.vision
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl http://localhost:20128/v1)
    (apiKeyEnvironmentVariable OMNIROUTE_API_KEY)
    (credentialBootstrap (
      (label "Create a workspace key from local OmniRoute")
      (url http://localhost:20128/api/keys)
      (method POST)
      (sessionLogin (
        (url http://localhost:20128/api/auth/login)
        (passwordEnvironmentVariable OMNIROUTE_ADMIN_PASSWORD)
        (defaultPassword CHANGEME)
        (requestField password)
      ))
      (request (
        (name MeTTaSymbolicLearnerWorkbench)
      ))
      (responseField key)
      (timeoutSeconds 10)
    ))
    (defaultModel auto/best-free)
    (timeoutSeconds 900)
  ))
  (aliases ([]))
  (categories ([]
    backends
    models
    reasoning
    systems/systems-llm
    todo-needs-categorization
    vision
  ))
  (dependedOnBy (
    (omniroute-free-router ())
  ))
  (implementedBy (
    (omniroute-free-router ())
  ))
  (inheritedBy (
    (omniroute-free-router (
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
  ))
)
