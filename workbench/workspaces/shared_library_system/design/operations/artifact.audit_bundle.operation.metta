(
  (id artifact.audit_bundle)
  (label "Audit Artifact Bundle")
  (description "Reusable consistency-audit operation migrated from the legacy ARC3 audit_artifact_bundle transaction.")
  (topics ([]
    artifacts
    symbolic
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (artifacts ArtifactBundle)
  ))
  (outputs (
    (audit Evidence)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      transaction_audit_artifact_bundle
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters (
    (requiresVision false)
  ))
  (kind operation)
)
