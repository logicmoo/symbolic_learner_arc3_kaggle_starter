(
  (id shared.generate_turtle)
  (label "Generate Turtle Program")
  (description "Generate an executable Turtle representation from entities and symbolic facts. Reusable for any grid or drawing domain.")
  (topics ([]
    graphics
    symbolic
  ))
  (implementation llm.turtle)
  (inputs (
    (entities EntityCollection)
    (facts (
      (datatype entity_collection)
      (representation symbolic_fact_set)
    ))
  ))
  (outputs (
    (programs TurtleProgramSet)
  ))
  (parameters ())
  (kind operation)
)
