(
  (kind operation)
  (id text_to_scene_graph)
  (label "Text to Scene Graph")
  (description "Convert an image represented as natural-language description into scene-graph representation.")
  (categories ([]
    text/understanding
    vision/conversion
    datatypes/representation
  ))
  (inputs (
    (image (
      (datatype image)
      (representation natural_language)
    ))
  ))
  (outputs (
    (image (
      (datatype image)
      (representation scene_graph)
    ))
  ))
  (conversion (
    (datatype image)
    (from natural_language)
    (to scene_graph)
  ))
)
