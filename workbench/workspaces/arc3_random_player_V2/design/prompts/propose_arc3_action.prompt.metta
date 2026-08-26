(
  (kind prompt)
  (id arc3_random.propose_action)
  (label "Propose an ARC3 Action")
  (description "Propose one legal action from current visual evidence and retained action outcomes.")
  (specializations (
    (arc3_random.propose_action.default (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (preferredSpecialization arc3_random.propose_action.default)
)
(
  (kind prompt)
  (id arc3_random.propose_action.default)
  (label "Propose an ARC3 Action — Default")
  (version 1)
  (targets ([]
    generic-chat
    vision-chat
  ))
  (implements (
    (arc3_random.propose_action (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (text ([]
    "Inspect the current ARC image, legal action table, state, and retained action statistics."
    "Choose one legal action. Prefer useful exploration and actions with better prior outcomes, but keep some randomness."
    "For complex actions include integer x and y coordinates from 0 through 63."
    "Return JSON with action, data, and reasoning."
  ))
)
