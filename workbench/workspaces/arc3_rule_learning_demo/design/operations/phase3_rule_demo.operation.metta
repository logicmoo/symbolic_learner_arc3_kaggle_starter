(
  (kind operation)
  (id phase3.apply_learned_rule)
  (label "Apply Learned Rule to Unseen Case")
  (description "Apply the selected learned transformation relative to a previously unseen object or state. Preserve the input identity and unrelated properties; numeric from/to pairs represent relative deltas unless the selected interpretation is explicitly absolute_target.")
  (topics ([]
    learning
    arc3
  ))
  (implementation llm.complete)
  (inputs (
    (rule Object)
    (unseen_case Object)
    (action Object)
  ))
  (outputs (
    (prediction Object)
  ))
  (modelSelection ((models ([] openrouter/free)) (strategy single)))
  (parameters ())
)

(
  (kind operation)
  (id phase3.grade_prediction)
  (label "Grade Prediction Against Independent Outcome")
  (description "Compare a prediction recorded before an outcome with a separately supplied observed outcome. Return success, failure, partial_match, contradiction, or ungradable plus attributable supporting or contradicting evidence; never award post-hoc prediction credit.")
  (topics ([]
    learning
    arc3
  ))
  (implementation llm.complete)
  (inputs (
    (prediction Object)
    (observed_outcome Object)
  ))
  (outputs (
    (grade Object)
  ))
  (modelSelection ((models ([] openrouter/free)) (strategy single)))
  (parameters ())
)
