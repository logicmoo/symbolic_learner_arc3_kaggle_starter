(
  (kind model_policy_variant)
  (id balanced_model_runtime)
  (label "Balanced Runtime")
  (description "General-purpose implementation of the default model-runtime policy. It balances measured quality, latency, cost, and reliability when ranking healthy eligible models, keeps automatic fallbacks available, and includes selected models in benchmark runs so future choices can use comparable evidence.")
  (enabled true)
  (example true)
  (selection (
    (strategy weighted)
    (fallback true)
    (weights (
      (quality 0.45)
      (latency 0.25)
      (cost 0.2)
      (reliability 0.1)
    ))
  ))
  (defaults (
    (wanted auto)
    (runtime auto)
    (benchmark on)
  ))
  (implements (
    (default_model_runtime (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
