# Policies

Policy resources are editable design artifacts stored as individual JSON files under `policies/`.

- `model_policy` defines an abstract runtime and benchmarking contract.
- `model_policy_variant` supplies an interchangeable strategy beneath a model policy.
- `vendor_policy` and `model_policy_entry` control wanted, runtime, and benchmark states.
- Health observations and ping records provide evidence; they do not silently rewrite user policy.
- Benchmark policies define matrices, metrics, repetitions, and eligible models.

Use the Enabled control for intentional activation. Use raw JSON for the complete resource. Workspace files override shared resources with the same ID.

[Repository guide](../../../../README.md)
