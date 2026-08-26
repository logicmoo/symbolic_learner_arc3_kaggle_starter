(
  (kind semantic_datatype)
  (id suggested_experiment)
  (label "Suggested Experiment")
  (description "A proposed observation or action intended to distinguish competing hypotheses or reduce uncertainty.")
  (runtimeContract (
    (shape map)
    (required ([]
      id
      instruction
    ))
    (properties (
      (id Text)
      (instruction Text)
      (rationale Text)
      (distinguishes ([]
        Text
      ))
      (expectedInformationGain Number)
      (risk Number)
    ))
  ))
  (implements (
    (information (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
