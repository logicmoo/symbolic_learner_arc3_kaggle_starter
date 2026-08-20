(
  (id symbolic.induce_rules)
  (label "Induce Rules from Symbolic Evidence")
  (description "Reusable rule-induction operation migrated from the legacy ARC3 induce_rules_from_prolog transaction.")
  (topics ([]
    symbolic
    learning
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (facts ArtifactBundle)
    (transitions ChangeDescription)
  ))
  (outputs (
    (rules RuleSet)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      rule_hypothesis
      symbolic_rule_evidence_schema
      transaction_induce_rules_from_symbolic
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters (
    (requiresVision false)
  ))
  (kind operation)
)
