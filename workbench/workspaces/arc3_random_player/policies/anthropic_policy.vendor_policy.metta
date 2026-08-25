(
  (kind vendor_policy)
  (id anthropic_policy)
  (vendorId anthropic)
  (label "Anthropic / Claude (disabled by default)")
  (description "Paid Anthropic Claude access is disabled in the shared free-first baseline. A workspace may explicitly override this policy after configuring its own key.")
  (enabled false)
  (policy (
    (wanted off)
    (runtime off)
    (benchmark off)
  ))
)
