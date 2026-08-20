(
  (kind operation)
  (id echo_into_titlecased_llm)
  (label "Echo Into Titlecased / LLM")
  (description "Take received text, send it through an LLM with the shared titlecase prompt, and return the title-cased text.")
  (topics ([]
    sample-demos
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (text Text)
  ))
  (outputs (
    (text Text)
  ))
  (modelSelection (
    (models ([]
      openrouter/free
    ))
    (strategy single)
  ))
  (bindings (
    (prompts ([]
      titlecase_received_text
    ))
    (separator "\n\n")
  ))
  (parameters (
    (inputBinding text)
    (outputBinding text)
  ))
  (parents ([]
    echo_into_titlecased
  ))
)
