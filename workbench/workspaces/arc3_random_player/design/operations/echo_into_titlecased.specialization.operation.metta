(
  (kind operation)
  (id echo_into_titlecased.specialization)
  (implements (
    (echo_into_titlecased ())
  ))
  (label "Echo Into Titlecased — Specialization")
  (description "Concrete Operation specialization.")
  (topics ([]
    text
    sample-demos
  ))
  (enabled true)
  (implementation python.callable)
  (inheritsFrom (
    (echo_into_titlecased (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
