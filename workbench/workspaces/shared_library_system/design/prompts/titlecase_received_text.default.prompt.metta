(
  (kind prompt)
  (id titlecase_received_text.default)
  (label "Titlecase Received Text — Default")
  (version 1)
  (targets ([]
    generic-chat
  ))
  (text ([]
    "Convert the received text to title case."
    "Preserve punctuation."
    "Return only the transformed text."
  ))
  (implements (
    (titlecase_received_text (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
