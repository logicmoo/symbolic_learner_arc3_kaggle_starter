(
  (id arc3.audit_artifact_bundle)
  (label "ARC3 Audit Artifact Bundle")
  (description "ARC3 wrapper around the shared artifact-audit operation, scoped to ARC3 object/Turtle/transition/rule artifacts.")
  (topics ([]
    arc3
    symbolic
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (bundle ArtifactBundle)
  ))
  (outputs (
    (audit_md (
      (datatype text)
      (representation plain_text)
      (concrete markdown)
    ))
  ))
  (bindings (
    (prompts ([]
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
    (domain arc3)
    (legacyTransaction audit_artifact_bundle)
    (artifactNames ([]
      object_registry.pl
      objects.pl
      differences.pl
      similarities.pl
      turtle_from_image.pl
      turtle_from_diff.pl
      rules.pl
    ))
  ))
  (kind operation)
)
