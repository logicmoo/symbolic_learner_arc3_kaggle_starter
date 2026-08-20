(
  (id vision.transition_analysis)
  (label "Vision Transition Analysis")
  (description "Compare before/after visual states, track objects, and describe observed changes without prematurely turning them into rules.")
  (topics ([]
    vision
    world-modeling
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (before Image)
    (after Image)
  ))
  (outputs (
    (changes ChangeDescription)
    (correspondences Object)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      logical_image_coordinates
      object_extraction
      transition_observation
      object_correspondence
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters ())
  (kind operation)
)
