(
  (kind prompt)
  (id output_quality_control)
  (label "Output Quality Control")
  (description "Generic final verification prompt for machine-readable visual/symbolic analysis outputs.")
  (text ([]
    "Before returning, verify that the output parses according to the requested machine-readable format."
    "Return only the requested fields and do not add Markdown wrappers unless explicitly requested."
    "Check coordinate conventions, identifier consistency, and syntax plausibility for any embedded executable or symbolic source."
  ))
  (metadata (
    (domain shared)
    (category quality-control)
  ))
)
