(
  (kind prompt)
  (id transaction_audit_artifact_bundle)
  (label "Audit Artifact Bundle")
  (description "Reusable artifact-consistency audit migrated from the legacy ARC3 workflow catalog.")
  (text ([]
    "Audit the supplied artifact bundle for internal consistency."
    "Check identifiers, coordinates, object facts, executable reconstructions, differences, correspondences, and inferred rules where present."
    "Report concrete inconsistencies and unsupported claims rather than silently repairing them."
  ))
  (metadata (
    (domain shared)
    (category artifact-audit)
  ))
)
