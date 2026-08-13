(
  (kind prompt_profile)
  (id vision_object_analysis)
  (label "Vision Object Analysis Prompt Profile")
  (description "Complete ordered composition for structured object extraction and executable reconstruction from a visual state.")
  (enabled true)
  (categories ([]
    prompts/composition
    vision/analysis
  ))
  (prompts ([]
    structured_json_response
    logical_image_coordinates
    object_extraction
    symbolic_scene_fact_schema
    turtle_reconstruction
    turtle_motion_dsl
    output_quality_control
  ))
  (separator "\n\n")
)
