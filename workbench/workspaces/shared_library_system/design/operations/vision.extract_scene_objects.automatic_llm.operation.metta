(
  (kind operation)
  (id vision.extract_scene_objects.automatic_llm)
  (label "Extract Scene Objects / Automatic LLM")
  (description "Send uploaded current and previous bitmap images through the shared extraction prompts using an automatically eligible vision LLM.")
  (topics ([]
    segmentation
    vision
    systems-llm
  ))
  (implementation llm.complete)
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
  (modelSelection (
    (strategy automatic)
    (requiredCapabilities ([]
      vision
    ))
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
  (parameters (
    (requiresVision true)
    (parseJson true)
    (responseFormat json_object)
  ))
  (implements (
    (vision.extract_scene_objects (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
