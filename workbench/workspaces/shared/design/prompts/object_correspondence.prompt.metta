({}
  (kind prompt)
  (id object_correspondence)
  (label "Object Correspondence")
  (description "Generic vision prompt for matching persistent objects across frames or states.")
  (text (
    "Establish before-to-after object correspondences only when supported by evidence."
    "Record persistent-object matches, similarity, matched properties, changed properties, and supporting evidence."
    "Do not force correspondence when appearance, disappearance, split, or merge is better supported."
  ))
  (metadata ({}
    (domain vision)
    (category tracking-and-correspondence)
  ))
)
