(
  (kind prompt)
  (id titlecase_received_text.text_only.claude)
  (label "Titlecase Received Text — Claude / Text Only")
  (description "Claude-specific text-only implementation of the Titlecase Received Text prompt contract.")
  (version 1)
  (targets ([]
    anthropic
    claude
  ))
  (metadata (
    (modelFamily claude)
    (modality text_only)
    (inputModalities ([]
      text
    ))
  ))
  (text ([]
    "Convert the supplied text to title case."
    "Keep the wording, punctuation, and spacing unchanged except where capitalization requires a change."
    "Do not explain the transformation."
    "Return only the converted text."
  ))
  (implements (
    (titlecase_received_text ())
  ))
  (inheritsFrom (
    (titlecase_received_text (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
