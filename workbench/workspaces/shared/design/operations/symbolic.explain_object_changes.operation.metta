(
  (id symbolic.explain_object_changes)
  (label "Explain Object Changes")
  (description "Reusable symbolic transition operation migrated from the legacy ARC3 explain_object_changes transaction.")
  (categories ([]
    symbolic/explanation
    world-modeling/transitions
    vision/transition
  ))
  (implementation llm.complete)
  (inputs (
    (objects (
      (datatype entity_collection)
      (representation object_list)
    ))
    (before ArtifactBundle)
    (after ArtifactBundle)
  ))
  (outputs (
    (changes ChangeDescription)
    (correspondences Object)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      transition_observation
      object_correspondence
      transaction_explain_object_changes
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
