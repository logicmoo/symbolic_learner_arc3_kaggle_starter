(
  (id arc3.explain_object_changes)
  (label "ARC3 Explain Object Changes")
  (description "ARC3 wrapper around shared symbolic transition analysis, adding ARC3 identity and artifact-file contracts.")
  (topics ([]
    arc3
    vision
    symbolic
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (object_registry FileReference)
    (objects ArtifactBundle)
    (before ArtifactBundle)
    (after ArtifactBundle)
  ))
  (outputs (
    (differences_pl PrologProgram)
    (similarities_pl PrologProgram)
    (turtle_from_diff_pl PrologProgram)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      arc3_response_contract
      arc3_identity_registry
      transition_observation
      object_correspondence
      transaction_explain_object_changes
      arc3_file_separation
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
    (legacyTransaction explain_object_changes)
  ))
  (kind operation)
)
