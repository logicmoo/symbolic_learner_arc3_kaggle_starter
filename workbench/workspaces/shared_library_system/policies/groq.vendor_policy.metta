(
  (kind vendor_policy)
  (id groq_policy)
  (vendorId groq)
  (label "Groq Cloud (disabled by default)")
  (description "Groq Cloud is disabled in the shared free-first baseline. A workspace may explicitly override this policy after confirming its own account and pricing.")
  (enabled false)
  (policy (
    (wanted off)
    (runtime off)
    (benchmark off)
  ))
)
