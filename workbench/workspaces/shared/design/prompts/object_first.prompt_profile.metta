(
  (kind prompt_profile)
  (id object_first)
  (label "Object-First Prompt Profile")
  (description "Compose reusable instructions for detecting objects before explaining their relationships or behavior.")
  (enabled true)
  (categories ([]
    prompts/composition
    vision/object-first
  ))
  (prompts ([]
    object_extraction
    logical_image_coordinates
    object_correspondence
    output_quality_control
  ))
  (separator "\n\n")
)
