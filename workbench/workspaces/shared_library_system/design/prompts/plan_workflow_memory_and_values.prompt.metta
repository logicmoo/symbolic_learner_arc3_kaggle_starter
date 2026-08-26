(
  (kind prompt)
  (id workflow.plan_memory_and_values)
  (label "Plan Workflow Memory and Values")
  (description "Derive explicit memory scopes, value lifecycles, iteration groups, persistence rules, and provenance requirements from a semantic workflow.")
  (specializations (
    (workflow.plan_memory_and_values.default (
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
  (preferredSpecialization workflow.plan_memory_and_values.default)
)
