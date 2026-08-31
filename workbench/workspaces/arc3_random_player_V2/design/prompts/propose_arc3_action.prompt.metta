(
  (kind prompt)
  (id arc3_random.propose_action)
  (label "Propose an ARC3 Action")
  (description "Propose one legal action from current visual evidence and retained action outcomes.")
  (implementedBy (
    (arc3_random.propose_action.default ())
  ))
  (inheritedBy (
    (arc3_random.propose_action.default (
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
  (preferredImplementation arc3_random.propose_action.default)
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
    (arc3_random.propose_action ())
  ))
  (text ([]
    "Inspect the current ARC image, legal action table, state, and retained action statistics."
    "Choose one legal action. Prefer useful exploration and actions with better prior outcomes, but keep some randomness."
    "For complex actions include integer x and y coordinates from 0 through 63."
    "Return JSON with action, data, and reasoning."
  ))
  (inheritsFrom (
    (arc3_random.propose_action (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
