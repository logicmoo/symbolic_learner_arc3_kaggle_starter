(
  (id vision.object_analysis)
  (label "Vision Object Analysis")
  (description "Analyze one visual state into structured objects and an executable reconstruction. This is the reusable vision core extracted from the older ARC3 prompt package.")
  (categories ([]
    vision/recognition
    vision/grouping
    graphics/reconstruction
  ))
  (implementation llm.complete)
  (inputs (
    (image Image)
  ))
  (outputs (
    (analysis Object)
    (reconstruction Program)
  ))
  (bindings (
    (promptProfiles ([]
      vision_object_analysis
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
