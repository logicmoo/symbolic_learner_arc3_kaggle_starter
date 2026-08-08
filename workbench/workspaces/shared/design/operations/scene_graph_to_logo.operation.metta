(
  (kind operation)
  (id scene_graph_to_logo)
  (label "Scene Graph to LOGO")
  (description "Convert an image from scene-graph representation to LOGO/Turtle representation.")
  (categories ([]
    vision/conversion
    graphics/turtle
    datatypes/representation
  ))
  (inputs (
    (image (
      (datatype image)
      (representation scene_graph)
    ))
  ))
  (outputs (
    (image (
      (datatype image)
      (representation logo_program)
    ))
  ))
  (conversion (
    (datatype image)
    (from scene_graph)
    (to logo_program)
  ))
)
