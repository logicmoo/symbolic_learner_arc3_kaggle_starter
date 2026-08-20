(
  (id vision.rule_learning)
  (label "Vision Rule Learning")
  (description "Infer candidate world rules from visual transitions while preserving evidence, alternatives, and contradictions.")
  (topics ([]
    vision
    symbolic
    learning
    systems-llm
  ))
  (implementation llm.complete)
  (inputs (
    (transitions ChangeDescription)
    (evidence Evidence)
  ))
  (outputs (
    (rules RuleSet)
  ))
  (bindings (
    (prompts ([]
      structured_json_response
      transition_observation
      object_correspondence
      rule_hypothesis
      symbolic_rule_evidence_schema
      output_quality_control
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters ())
  (kind operation)
)
