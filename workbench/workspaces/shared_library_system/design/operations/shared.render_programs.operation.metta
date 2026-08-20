(
  (id shared.render_programs)
  (label "Render Executable Programs")
  (description "Execute symbolic drawing programs and produce a reconstructed observation. Generic rendering operation.")
  (topics ([]
    graphics
    symbolic
  ))
  (implementation turtle.runtime)
  (inputs (
    (programs TurtleProgramSet)
  ))
  (outputs (
    (reconstruction Observation)
  ))
  (parameters ())
  (kind operation)
)
