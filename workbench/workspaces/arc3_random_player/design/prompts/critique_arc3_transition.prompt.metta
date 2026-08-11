(
  (kind prompt)
  (id arc3_random.critique_transition)
  (label "Critique an ARC3 Transition")
  (description "Classify what an action did well or poorly using before/after evidence.")
  (children ([] arc3_random.critique_transition.default))
  (preferredChild arc3_random.critique_transition.default)
)
(
  (kind prompt)
  (id arc3_random.critique_transition.default)
  (label "Critique an ARC3 Transition — Default")
  (version 1)
  (targets ([] generic-chat vision-chat))
  (parents ([] arc3_random.critique_transition))
  (text ([]
    "Compare the before and after ARC observations and the chosen action."
    "Classify the result as good, bad, or neutral. Wins and level progress are good; game-over and ineffective repeated moves are bad."
    "State the visible evidence and a concise lesson that can guide a later attempt."
    "Return JSON with rating, reason, evidence, and lesson."
  ))
)
