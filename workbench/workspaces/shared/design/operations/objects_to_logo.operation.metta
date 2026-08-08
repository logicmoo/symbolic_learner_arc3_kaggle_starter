({}
  (kind operation)
  (id objects_to_logo)
  (label "Objects to LOGO")
  (description "Convert an image from object-list representation to LOGO/Turtle representation.")
  (categories (
    vision/conversion
    graphics/turtle
    datatypes/representation
  ))
  (inputs ({}
    (image ({}
      (datatype image)
      (representation object_list)
    ))
  ))
  (outputs ({}
    (image ({}
      (datatype image)
      (representation logo_program)
    ))
  ))
  (conversion ({}
    (datatype image)
    (from object_list)
    (to logo_program)
  ))
)
