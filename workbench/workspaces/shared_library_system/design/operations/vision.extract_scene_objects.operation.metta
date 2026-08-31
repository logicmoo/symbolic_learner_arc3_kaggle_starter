(
  (id vision.extract_scene_objects)
  (label "Extract Scene Objects")
  (description "Reusable vision operation migrated from the legacy ARC extract_scene_objects transaction.")
  (topics ([]
    segmentation
    vision
  ))
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
  (implementedBy (
    (vision.extract_scene_objects.automatic_llm ())
  ))
  (inheritedBy (
    (vision.extract_scene_objects.automatic_llm (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (preferredImplementation vision.extract_scene_objects.automatic_llm)
)
