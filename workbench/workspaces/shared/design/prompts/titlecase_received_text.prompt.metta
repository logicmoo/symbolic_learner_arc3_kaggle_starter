(
  (kind prompt)
  (id titlecase_received_text)
  (label "Titlecase Received Text")
  (description "Transform received text to title case without coupling the operation to a specific model prompt.")
  (inputs (
    (text text)
  ))
  (outputs (
    (text text)
  ))
  (children ([]
    titlecase_received_text.default
    titlecase_received_text.gpt5
    titlecase_received_text.multi_modal.claude
    titlecase_received_text.text_only.claude
  ))
  (preferredChild titlecase_received_text.default)
  (example_execute (
    (action prompt.render)
    (arguments (
      (text (
        (datatype Text)
        (label "Received text")
        (default "the quick brown fox")
      ))
    ))
  ))
)
