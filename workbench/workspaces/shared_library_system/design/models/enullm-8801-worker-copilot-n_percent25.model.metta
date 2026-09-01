(
  (kind model)
  (id enullm-8801-worker-copilot-n_percent25)
  (label "Copilot pool N · (~25% capable)")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (inheritsFrom (
    (enullm-8801 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (dependsOn (
    (enullm-8801 ())
  ))
  (model worker-copilot-n/percent25)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (imageGeneration false)
    (imageOutput false)
    (local true)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 200000)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id worker-copilot-n/percent25)
    (object model)
    (display_name "Copilot pool N · (~25% capable)")
    (description "Client-affine Copilot pool alias. Literal n is assigned by client IP and 1024-port source range; replace n with any positive integer to address or create that exact worker.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by emullm-copilot-pool)
    (connected true)
    (worker_id worker-copilot-n)
    (worker_kind null)
    (backing_model null)
    (simulated true)
    (active_workers ([]
      worker-copilot-1
      worker-copilot-10
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-2
      worker-copilot-20
      worker-copilot-21
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (routing_mode client_ip_port_range_affinity)
    (affinity_port_range_size 1024)
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (ownedBy emullm-copilot-pool)
  ))
  (providerMetadata (
    (id worker-copilot-n/percent25)
    (object model)
    (display_name "Copilot pool N · (~25% capable)")
    (description "Client-affine Copilot pool alias. Literal n is assigned by client IP and 1024-port source range; replace n with any positive integer to address or create that exact worker.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by emullm-copilot-pool)
    (connected true)
    (worker_id worker-copilot-n)
    (worker_kind null)
    (backing_model null)
    (simulated true)
    (active_workers ([]
      worker-copilot-1
      worker-copilot-10
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-2
      worker-copilot-20
      worker-copilot-21
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (routing_mode client_ip_port_range_affinity)
    (affinity_port_range_size 1024)
    (assigned_worker_header X-EmuLLM-Worker-ID)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-n/percent25)
  ))
)
