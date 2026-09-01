(
  (kind model)
  (id enullm-8801-copilot_claude-sonnet-4.5)
  (label "GitHub Copilot · Claude Sonnet 4.5")
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
  (model copilot/claude-sonnet-4.5)
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
    (maxOutputTokens 32000)
  ))
  (pricing ())
  (properties (
    (id copilot/claude-sonnet-4.5)
    (name "Claude Sonnet 4.5")
    (capabilities (
      (family claude-sonnet-4.5)
      (limits (
        (max_context_window_tokens 200000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 32000)
        (max_prompt_tokens 168000)
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
        (inputPrice 300)
        (outputPrice 1500)
        (cachePrice 30)
        (cacheReadPrice 30)
        (cacheWritePrice 375)
        (batchSize 1000000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Sonnet 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Sonnet 4.5](https://docs.github.com/en/copilot/using-github-copilot/ai-models/using-claude-sonnet-in-github-copilot).")
    ))
    (quality_rank 18)
    (quality_tier versatile)
    (object model)
    (display_name "GitHub Copilot · Claude Sonnet 4.5")
    (description "Authenticated GitHub Copilot backing model 'claude-sonnet-4.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model claude-sonnet-4.5)
    (connected true)
    (active_workers ([]
      worker-copilot-2
    ))
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
      (id claude-sonnet-4.5)
      (name "Claude Sonnet 4.5")
      (capabilities (
        (family claude-sonnet-4.5)
        (limits (
          (max_context_window_tokens 200000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 32000)
          (max_prompt_tokens 168000)
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
          (inputPrice 300)
          (outputPrice 1500)
          (cachePrice 30)
          (cacheReadPrice 30)
          (cacheWritePrice 375)
          (batchSize 1000000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Sonnet 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Sonnet 4.5](https://docs.github.com/en/copilot/using-github-copilot/ai-models/using-claude-sonnet-in-github-copilot).")
      ))
      (quality_rank 18)
      (quality_tier versatile)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/claude-sonnet-4.5)
    (name "Claude Sonnet 4.5")
    (capabilities (
      (family claude-sonnet-4.5)
      (limits (
        (max_context_window_tokens 200000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 32000)
        (max_prompt_tokens 168000)
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
        (inputPrice 300)
        (outputPrice 1500)
        (cachePrice 30)
        (cacheReadPrice 30)
        (cacheWritePrice 375)
        (batchSize 1000000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Sonnet 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Sonnet 4.5](https://docs.github.com/en/copilot/using-github-copilot/ai-models/using-claude-sonnet-in-github-copilot).")
    ))
    (quality_rank 18)
    (quality_tier versatile)
    (object model)
    (display_name "GitHub Copilot · Claude Sonnet 4.5")
    (description "Authenticated GitHub Copilot backing model 'claude-sonnet-4.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model claude-sonnet-4.5)
    (connected true)
    (active_workers ([]
      worker-copilot-2
    ))
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
      (id claude-sonnet-4.5)
      (name "Claude Sonnet 4.5")
      (capabilities (
        (family claude-sonnet-4.5)
        (limits (
          (max_context_window_tokens 200000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 32000)
          (max_prompt_tokens 168000)
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
          (inputPrice 300)
          (outputPrice 1500)
          (cachePrice 30)
          (cacheReadPrice 30)
          (cacheWritePrice 375)
          (batchSize 1000000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Sonnet 4.5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Sonnet 4.5](https://docs.github.com/en/copilot/using-github-copilot/ai-models/using-claude-sonnet-in-github-copilot).")
      ))
      (quality_rank 18)
      (quality_tier versatile)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/claude-sonnet-4.5)
  ))
)
