(
  (kind prompt)
  (id workflow.generate_from_english)
  (label "Generate Workflow from English")
  (description "Author one grounded Workflow object from an English specification without inventing resources.")
  (implementedBy (
    (workflow.generate_from_english.metta ())
    (workflow.generate_from_english.json ())
  ))
  (inheritedBy (
    (workflow.generate_from_english.metta (
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
    (workflow.generate_from_english.json (
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
  (preferredImplementation workflow.generate_from_english.json)
)
