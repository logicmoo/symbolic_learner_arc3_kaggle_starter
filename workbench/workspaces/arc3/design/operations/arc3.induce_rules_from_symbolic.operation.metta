(
  (id arc3.induce_rules_from_symbolic)
  (label "ARC3 Induce Rules from Symbolic Evidence")
  (description "ARC3 wrapper around shared rule induction, adding ARC3 identity and rules.pl output contracts.")
  (categories ([]
    arc3/learning
    symbolic/rule-learning
  ))
  (implementation llm.complete)
  (inputs (
    (object_registry FileReference)
    (artifacts ArtifactBundle)
  ))
  (outputs (
    (rules_pl PrologProgram)
  ))
  (promptSelection (
    (prompts ([]
      structured_json_response
      arc3_response_contract
      arc3_identity_registry
      rule_hypothesis
      symbolic_rule_evidence_schema
      transaction_induce_rules_from_symbolic
      arc3_file_separation
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters (
    (domain arc3)
    (legacyTransaction induce_rules_from_prolog)
  ))
  (kind operation)
)
