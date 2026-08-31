(
  (kind model_policy)
  (id default_model_runtime)
  (label "Default Model Runtime Policy")
  (description "Defines the shared contract for model selection without naming a specific provider or model. It separates user intent (wanted, runtime, and benchmark states) from observed vendor and model health, then applies health thresholds and fallback rules when effective eligibility is calculated. Enabled variants implement this policy with different selection priorities.")
  (enabled true)
  (example true)
  (rules (
    (requireHealthyVendor true)
    (requireHealthyModel true)
    (allowWantedAuto true)
    (excludeSlowFromRuntime true)
    (slowLatencyMs 5000)
    (maxFailureRate 0.2)
    (continueConcurrentPingsOnFailure true)
  ))
  (implementedBy (
    (balanced_model_runtime ())
    (economy_model_runtime ())
  ))
  (inheritedBy (
    (balanced_model_runtime (
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
    (economy_model_runtime (
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
  (preferredImplementation balanced_model_runtime)
)
