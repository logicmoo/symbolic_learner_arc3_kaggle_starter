({}
  (kind prompt)
  (id arc3_identity_registry)
  (label "ARC3 Identity Registry")
  (description "ARC3-specific canonical object identity rules.")
  (text (
    "object_registry.pl is the canonical identity source. Reuse every established friendly ID exactly."
    "new_identities must contain only genuinely new semantic objects, each represented with id, type, and label."
    "Do not invent opaque IDs such as obj_1 or object_7 and do not repeat established object_identity/3 declarations in objects_pl."
  ))
  (metadata ({}
    (domain arc3)
    (category identity)
  ))
)
