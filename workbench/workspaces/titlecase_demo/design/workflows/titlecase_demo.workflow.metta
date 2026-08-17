(
  (kind workflow)
  (id titlecase_demo)
  (label "Titlecase Demo")
  (description "Minimal workflow demonstrating an abstract operation resolved to a concrete implementation at runtime.")
  (generation (
    (operation workflow.populate_from_english)
    (englishDescriptionPath docs/WORKFLOW_DESCRIPTION.md)
    (operationCategories ([] workflow-language))
    (preflightRequired true)
  ))
  (inputs (
    (text Text)
  ))
  (outputs (
    (text $titlecased_text)
  ))
  (steps ([]
    (
      (kind workflow_step)
      (id step_titlecase)
      (operation echo_into_titlecased)
      (inputs (
        (text $text)
      ))
      (outputs (
        (text titlecased_text)
      ))
    )
  ))
)
