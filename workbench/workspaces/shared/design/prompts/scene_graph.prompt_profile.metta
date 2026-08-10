(
  (kind prompt_profile)
  (id scene_graph)
  (label "Scene-Graph Prompt Profile")
  (description "Compose reusable instructions for structured scene facts, coordinates, and relationship-aware output.")
  (enabled true)
  (categories ([]
    prompts/composition
    vision/scene-graph
  ))
  (prompts ([]
    symbolic_scene_fact_schema
    logical_image_coordinates
    structured_json_response
    output_quality_control
  ))
  (separator "\n\n")
)
