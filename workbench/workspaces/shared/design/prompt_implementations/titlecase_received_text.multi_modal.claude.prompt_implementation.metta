(
  (kind prompt_implementation)
  (id titlecase_received_text.multi_modal.claude)
  (label "Titlecase Received Text — Claude / Multi-Modal")
  (description "Claude-specific multi-modal implementation of the Titlecase Received Text prompt contract for contexts where the text may be accompanied by visual input.")
  (version 1)
  (targets ([]
    anthropic
    claude
  ))
  (metadata (
    (modelFamily claude)
    (modality multi_modal)
    (inputModalities ([]
      text
      image
    ))
  ))
  (text ([]
    "Convert the supplied text to title case."
    "Visual context may be present, but use it only to disambiguate the supplied text; do not describe the image."
    "Keep the wording and punctuation unchanged except where capitalization requires a change."
    "Do not explain the transformation."
    "Return only the converted text."
  ))
  (parents ([]
    titlecase_received_text
  ))
)
