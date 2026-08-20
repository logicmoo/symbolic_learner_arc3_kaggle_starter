(
  (id vision.extract_scene_objects)
  (label "Extract Scene Objects")
  (description "Reusable vision operation migrated from the legacy ARC extract_scene_objects transaction.")
  (categories ([]
    vision/extraction
    vision/recognition
    vision/grouping
  ))
  (subjects ([]
    segmentation
    vision
  ))
  (children ([]
    vision.extract_scene_objects.automatic_llm
  ))
  (preferredChild vision.extract_scene_objects.automatic_llm)
  (inputs (
    (current_image Image)
    (previous_image Image)
  ))
  (outputs (
    (objects (
      (datatype entity_collection)
      (representation object_list)
    ))
    (reconstruction Program)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      logical_image_coordinates
      object_extraction
      symbolic_scene_fact_schema
      turtle_reconstruction
      turtle_motion_dsl
      transaction_extract_scene_objects
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters (
    (requiresVision true)
  ))
  (kind operation)
)
