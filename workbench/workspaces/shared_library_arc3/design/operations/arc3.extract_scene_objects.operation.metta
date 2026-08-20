(
  (id arc3.extract_scene_objects)
  (label "ARC3 Extract Scene Objects")
  (description "ARC3 wrapper around the shared visual object-extraction capability, adding only ARC3 identity/output/file contracts.")
  (topics ([]
    arc3
    segmentation
    vision
  ))
  (implementation llm.complete)
  (inputs (
    (current_image Image)
    (parent_image Image)
    (object_registry FileReference)
  ))
  (outputs (
    (objects_pl PrologProgram)
    (turtle_from_image_pl PrologProgram)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      arc3_response_contract
      logical_image_coordinates
      arc3_identity_registry
      object_extraction
      symbolic_scene_fact_schema
      turtle_reconstruction
      turtle_motion_dsl
      transaction_extract_scene_objects
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
    (legacyTransaction extract_scene_objects)
  ))
  (kind operation)
)
