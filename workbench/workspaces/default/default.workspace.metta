(
  (kind workspace)
  (id default)
  (label Default)
  (description "Minimal starter workspace. Add project-specific resources here; reusable resources are inherited from Shared.")
  (includes ([]
    (
      (workspaceId shared_library_system)
      (includeInherited true)
    )
  ))
)
