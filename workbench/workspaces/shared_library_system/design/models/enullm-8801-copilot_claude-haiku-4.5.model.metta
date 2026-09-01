(
  (kind model)
  (id enullm-8801-copilot_claude-haiku-4.5)
  (label "GitHub Copilot · Claude Haiku 4.5")
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
  (model copilot/claude-haiku-4.5)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (imageGeneration false)
    (imageOutput false)
    (local true)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 200000)
    (maxOutputTokens 64000)
  ))
  (pricing ())
  (properties (
    (id copilot/claude-haiku-4.5)
    (name "Claude Haiku 4.5")
    (capabilities (
      (family claude-haiku-4.5)
      (limits (
        (max_context_window_tokens 200000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 64000)
        (max_prompt_tokens 136000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 5)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (max_thinking_budget 32000)
        (min_thinking_budget 1024)
        (parallel_tool_calls true)
        (streaming true)
        (tool_calls true)
        (vision true)
        (adaptive_thinking unsupported)
        (reasoningEffort false)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 100)
        (outputPrice 500)
        (cachePrice 10)
        (cacheReadPrice 10)
        (cacheWritePrice 125)
        (batchSize 1000000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Haiku 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Haiku 4.5](https://gh.io/copilot-anthropic).")
    ))
    (quality_rank 24)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · Claude Haiku 4.5")
    (description "Authenticated GitHub Copilot backing model 'claude-haiku-4.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model claude-haiku-4.5)
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
          application/pdf
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
      (id claude-haiku-4.5)
      (name "Claude Haiku 4.5")
      (capabilities (
        (family claude-haiku-4.5)
        (limits (
          (max_context_window_tokens 200000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 64000)
          (max_prompt_tokens 136000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 5)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (max_thinking_budget 32000)
          (min_thinking_budget 1024)
          (parallel_tool_calls true)
          (streaming true)
          (tool_calls true)
          (vision true)
          (adaptive_thinking unsupported)
          (reasoningEffort false)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 100)
          (outputPrice 500)
          (cachePrice 10)
          (cacheReadPrice 10)
          (cacheWritePrice 125)
          (batchSize 1000000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Haiku 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Haiku 4.5](https://gh.io/copilot-anthropic).")
      ))
      (quality_rank 24)
      (quality_tier lightweight)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/claude-haiku-4.5)
    (name "Claude Haiku 4.5")
    (capabilities (
      (family claude-haiku-4.5)
      (limits (
        (max_context_window_tokens 200000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 64000)
        (max_prompt_tokens 136000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 5)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (max_thinking_budget 32000)
        (min_thinking_budget 1024)
        (parallel_tool_calls true)
        (streaming true)
        (tool_calls true)
        (vision true)
        (adaptive_thinking unsupported)
        (reasoningEffort false)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 100)
        (outputPrice 500)
        (cachePrice 10)
        (cacheReadPrice 10)
        (cacheWritePrice 125)
        (batchSize 1000000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Haiku 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Haiku 4.5](https://gh.io/copilot-anthropic).")
    ))
    (quality_rank 24)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · Claude Haiku 4.5")
    (description "Authenticated GitHub Copilot backing model 'claude-haiku-4.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model claude-haiku-4.5)
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
          application/pdf
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
      (id claude-haiku-4.5)
      (name "Claude Haiku 4.5")
      (capabilities (
        (family claude-haiku-4.5)
        (limits (
          (max_context_window_tokens 200000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 64000)
          (max_prompt_tokens 136000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 5)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (max_thinking_budget 32000)
          (min_thinking_budget 1024)
          (parallel_tool_calls true)
          (streaming true)
          (tool_calls true)
          (vision true)
          (adaptive_thinking unsupported)
          (reasoningEffort false)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 100)
          (outputPrice 500)
          (cachePrice 10)
          (cacheReadPrice 10)
          (cacheWritePrice 125)
          (batchSize 1000000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Haiku 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Haiku 4.5](https://gh.io/copilot-anthropic).")
      ))
      (quality_rank 24)
      (quality_tier lightweight)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/claude-haiku-4.5)
  ))
)
