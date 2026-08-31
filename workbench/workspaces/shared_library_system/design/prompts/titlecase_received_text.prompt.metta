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
  (implementedBy (
    (titlecase_received_text.default ())
    (titlecase_received_text.gpt5 ())
    (titlecase_received_text.multi_modal.claude ())
    (titlecase_received_text.text_only.claude ())
  ))
  (inheritedBy (
    (titlecase_received_text.default (
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
    (titlecase_received_text.gpt5 (
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
    (titlecase_received_text.multi_modal.claude (
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
    (titlecase_received_text.text_only.claude (
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
  (preferredImplementation titlecase_received_text.default)
)
