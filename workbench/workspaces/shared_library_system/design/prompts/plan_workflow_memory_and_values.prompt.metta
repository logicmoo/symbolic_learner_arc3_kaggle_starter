(
  (kind prompt)
  (id workflow.plan_memory_and_values)
  (label "Plan Workflow Memory and Values")
  (description "Derive explicit memory scopes, value lifecycles, iteration groups, persistence rules, and provenance requirements from a semantic workflow.")
  (implementedBy (
    (workflow.plan_memory_and_values.default ())
  ))
  (inheritedBy (
    (workflow.plan_memory_and_values.default (
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
  (preferredImplementation workflow.plan_memory_and_values.default)
)
