({}
  (kind model_ping_job)
  (id example_vendor_ping)
  (label "Example Concurrent Vendor Ping")
  (description "Example record of a bounded concurrent health-check job. It identifies the model targets, timeout, concurrency, and error-continuation behavior used for one run; disabling the resource prevents it from being treated as a scheduled job while preserving it as an inspectable example and execution record.")
  (enabled false)
  (example true)
  (status completed)
  (targets (
    openai:gpt-5.6
  ))
  (concurrency 4)
  (timeoutMs 15000)
  (continueOnError true)
  (createdAt 2026-08-08T00:00:00Z)
  (completedAt 2026-08-08T00:00:00Z)
)
