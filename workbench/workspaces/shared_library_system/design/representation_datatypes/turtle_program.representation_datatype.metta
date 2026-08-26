(
  (kind representation_datatype)
  (id turtle_program)
  (label "Turtle Program")
  (language logo)
  (description "Movement-based Turtle/LOGO program representation retained as a first-class alias used by existing operations.")
  (implements (
    (image (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (specializations (
    (turtle_source (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization turtle_source)
)
