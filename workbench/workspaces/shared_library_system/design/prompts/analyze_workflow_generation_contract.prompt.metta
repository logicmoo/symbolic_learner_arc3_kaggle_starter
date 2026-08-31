(
  (kind prompt)
  (id workflow.analyze_generation_contract)
  (label "Analyze Workflow Generation Contract")
  (description "Build the complete Generation Contract from English in one call while preserving the requested experimental section order.")
  (implementedBy (
    (workflow.analyze_generation_contract.json ())
  ))
  (inheritedBy (
    (workflow.analyze_generation_contract.json (
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
  (preferredImplementation workflow.analyze_generation_contract.json)
)
