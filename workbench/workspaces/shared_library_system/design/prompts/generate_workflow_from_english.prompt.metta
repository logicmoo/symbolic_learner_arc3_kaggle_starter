(
  (kind prompt)
  (id workflow.generate_from_english)
  (label "Generate Workflow from English")
  (description "Author one grounded Workflow object from an English specification without inventing resources.")
  (specializations (
    (workflow.generate_from_english.metta (
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
    (workflow.generate_from_english.json (
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
  (preferredSpecialization workflow.generate_from_english.json)
)
