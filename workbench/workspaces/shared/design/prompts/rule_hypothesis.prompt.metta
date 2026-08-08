({}
  (kind prompt)
  (id rule_hypothesis)
  (label "Rule Hypothesis")
  (description "Generic reasoning prompt for separating observed regularities from hypotheses and their evidence.")
  (text (
    "Separate directly observed regularities from hypothetical rules."
    "Every hypothesis should identify its assumptions or unresolved alternatives and cite concrete supporting evidence."
    "Track contradictory evidence separately from supporting evidence."
    "Do not promote a hypothesis to an observed rule from a single ambiguous coincidence."
  ))
  (metadata ({}
    (domain shared)
    (category rule-learning)
  ))
)
