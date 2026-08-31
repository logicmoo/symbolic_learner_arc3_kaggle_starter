(
  (kind operation)
  (id echo_into_titlecased)
  (label "Echo Into Titlecased")
  (description "Take received text and return the title-cased text.")
  (topics ([]
    text
    sample-demos
  ))
  (role abstract_stage)
  (inputs (
    (text Text)
  ))
  (outputs (
    (text Text)
  ))
  (example_execute (
    (action operation.invoke)
    (arguments (
      (text (
        (datatype Text)
        (label "Text to title-case")
        (default "the quick brown fox")
      ))
    ))
  ))
  (implementedBy (
    (echo_into_titlecased_llm ())
    (echo_into_titlecased_prolog ())
    (echo_into_titlecased_python ())
    (echo_into_titlecased.specialization ())
  ))
  (inheritedBy (
    (echo_into_titlecased_llm (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (echo_into_titlecased_prolog (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (echo_into_titlecased_python (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (echo_into_titlecased.specialization (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (preferredImplementation echo_into_titlecased_python)
)
