(
  (id arc3.symbolic_state_analysis.deep)
  (label "ARC3 Symbolic State Analysis — deep")
  (description "Legacy deep ARC3 prompt composition expressed correctly as a Operation; adds cross-state correspondence without the extreme rule-hypothesis pass.")
  (categories ([]
    arc3/analysis
    vision/transition
    sample/arc3
  ))
  (implementation llm.complete)
  (inputs (
    (current_image Image)
    (parent_image Image)
    (object_registry FileReference)
  ))
  (outputs (
    (analysis ArtifactBundle)
  ))
  (promptSelection (
    (prompts ([]
      structured_json_response
      arc3_response_contract
      logical_image_coordinates
      arc3_identity_registry
      object_extraction
      turtle_reconstruction
      transition_observation
      object_correspondence
      arc3_file_separation
      arc3_root_state
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
    (analysisTier deep)
  ))
  (kind operation)
)
