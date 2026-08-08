({}
  (id shared.extract_entities)
  (label "Extract Entities")
  (description "Extract candidate entities or connected components from an observation. Generic perception operation reusable across visual worlds.")
  (categories (
    vision/extraction
    vision/grouping
    world-modeling/entities
  ))
  (implementation vision.segment)
  (inputs ({}
    (observation Observation)
  ))
  (outputs ({}
    (entities EntitySet)
  ))
  (parameters ({}))
  (kind operation)
)
