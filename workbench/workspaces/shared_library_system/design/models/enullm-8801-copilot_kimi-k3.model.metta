(
  (kind model)
  (id enullm-8801-copilot_kimi-k3)
  (label "GitHub Copilot · Kimi K3")
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
  (model copilot/kimi-k3)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (imageGeneration false)
    (imageOutput false)
    (local true)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 131072)
  ))
  (pricing ())
  (properties (
    (id copilot/kimi-k3)
    (name "Kimi K3")
    (capabilities (
      (family kimi-k3)
      (limits (
        (max_context_window_tokens 1048576)
        (max_output_tokens 131072)
        (max_prompt_tokens 917504)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/gif
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          high
          max
        ))
        (streaming true)
        (structured_outputs true)
        (tool_calls true)
        (vision true)
        (adaptive_thinking unsupported)
        (reasoningEffort true)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 300)
        (outputPrice 1500)
        (cachePrice 30)
        (cacheReadPrice 30)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 917504)
        (maxPromptTokens 917504)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to Kimi K3 from Moonshot AI.")
    ))
    (quality_rank 8)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · Kimi K3")
    (description "Authenticated GitHub Copilot backing model 'kimi-k3'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1048576)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model kimi-k3)
    (connected false)
    (active_workers ([]))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (input_modalities (
      (attachment_transport (
        (supported true)
        (source "Copilot SDK blob attachments via EMULLM cloud-file transport")
        (media_types ([]
          */*
        ))
      ))
      (image (
        (status sdk_advertised)
        (media_types ([]
          image/jpeg
          image/png
          image/webp
          image/gif
        ))
        (enabled true)
      ))
      (audio (
        (status not_advertised)
        (source "Copilot SDK schema has no audio capability field")
        (media_types ([]))
        (transport_supported true)
        (enabled false)
      ))
      (general_file (
        (status transport_supported)
        (model_comprehension model-dependent)
        (enabled true)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
        (status not_advertised)
      ))
      (image_generation (
        (enabled false)
        (status not_advertised)
      ))
      (image_output (
        (enabled false)
        (status not_advertised)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled false)
        (capability image_output)
        (status not_advertised)
        (media_types ([]))
      ))
    ))
    (backingModelMetadata (
      (id kimi-k3)
      (name "Kimi K3")
      (capabilities (
        (family kimi-k3)
        (limits (
          (max_context_window_tokens 1048576)
          (max_output_tokens 131072)
          (max_prompt_tokens 917504)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/gif
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            high
            max
          ))
          (streaming true)
          (structured_outputs true)
          (tool_calls true)
          (vision true)
          (adaptive_thinking unsupported)
          (reasoningEffort true)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 300)
          (outputPrice 1500)
          (cachePrice 30)
          (cacheReadPrice 30)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 917504)
          (maxPromptTokens 917504)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to Kimi K3 from Moonshot AI.")
      ))
      (quality_rank 8)
      (quality_tier powerful)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/kimi-k3)
    (name "Kimi K3")
    (capabilities (
      (family kimi-k3)
      (limits (
        (max_context_window_tokens 1048576)
        (max_output_tokens 131072)
        (max_prompt_tokens 917504)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/gif
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          high
          max
        ))
        (streaming true)
        (structured_outputs true)
        (tool_calls true)
        (vision true)
        (adaptive_thinking unsupported)
        (reasoningEffort true)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 300)
        (outputPrice 1500)
        (cachePrice 30)
        (cacheReadPrice 30)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 917504)
        (maxPromptTokens 917504)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to Kimi K3 from Moonshot AI.")
    ))
    (quality_rank 8)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · Kimi K3")
    (description "Authenticated GitHub Copilot backing model 'kimi-k3'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1048576)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model kimi-k3)
    (connected false)
    (active_workers ([]))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (input_modalities (
      (attachment_transport (
        (supported true)
        (source "Copilot SDK blob attachments via EMULLM cloud-file transport")
        (media_types ([]
          */*
        ))
      ))
      (image (
        (status sdk_advertised)
        (media_types ([]
          image/jpeg
          image/png
          image/webp
          image/gif
        ))
        (enabled true)
      ))
      (audio (
        (status not_advertised)
        (source "Copilot SDK schema has no audio capability field")
        (media_types ([]))
        (transport_supported true)
        (enabled false)
      ))
      (general_file (
        (status transport_supported)
        (model_comprehension model-dependent)
        (enabled true)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
        (status not_advertised)
      ))
      (image_generation (
        (enabled false)
        (status not_advertised)
      ))
      (image_output (
        (enabled false)
        (status not_advertised)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled false)
        (capability image_output)
        (status not_advertised)
        (media_types ([]))
      ))
    ))
    (backingModelMetadata (
      (id kimi-k3)
      (name "Kimi K3")
      (capabilities (
        (family kimi-k3)
        (limits (
          (max_context_window_tokens 1048576)
          (max_output_tokens 131072)
          (max_prompt_tokens 917504)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/gif
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            high
            max
          ))
          (streaming true)
          (structured_outputs true)
          (tool_calls true)
          (vision true)
          (adaptive_thinking unsupported)
          (reasoningEffort true)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 300)
          (outputPrice 1500)
          (cachePrice 30)
          (cacheReadPrice 30)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 917504)
          (maxPromptTokens 917504)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to Kimi K3 from Moonshot AI.")
      ))
      (quality_rank 8)
      (quality_tier powerful)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/kimi-k3)
  ))
)
