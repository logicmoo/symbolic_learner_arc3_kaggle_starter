({}
  (kind prompt)
  (id transaction_extract_scene_objects)
  (label "Extract Stable Scene Objects")
  (description "Reusable vision transaction prompt migrated from the legacy ARC3 workflow catalog.")
  (text (
    "Extract stable semantic objects from the requested before/current images."
    "Concentrate on object identity, geometry, topology, color, role, and motion-relevant substructure."
    "Return only the artifact fields requested by the operation."
  ))
  (metadata ({}
    (domain vision)
    (category transaction)
  ))
)
