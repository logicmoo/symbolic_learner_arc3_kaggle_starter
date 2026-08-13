(
  (kind prompt)
  (id arc3_response_contract)
  (label "ARC3 Response Contract")
  (description "ARC3-specific output contract layered on the shared structured JSON prompt.")
  (text ([]
    "Analyze the current ARC3 state and return exactly the dynamically requested subset of these allowed keys: new_identities, objects_pl, differences_pl, similarities_pl, turtle_from_image_pl, turtle_from_diff_pl, and rules_pl."
    "new_identities must be a JSON array. Every *_pl value must be a JSON string containing plain SWI-Prolog source."
  ))
  (metadata (
    (domain arc3)
    (category output-contract)
    (uses ([]
      structured_json_response
    ))
  ))
)
