(
  (kind prompt)
  (id workflow.generate_from_english)
  (label "Generate Workflow from English")
  (description "Author one grounded Workflow object from an English specification without inventing resources.")
  (children ([] workflow.generate_from_english.metta workflow.generate_from_english.json))
  (preferredChild workflow.generate_from_english.json)
)
