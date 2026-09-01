(
  (kind model)
  (id enullm-8801-copilot_kimi-k2.7-code)
  (label "GitHub Copilot · Kimi K2.7 Code")
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
  (model copilot/kimi-k2.7-code)
  (enabled true)
  (capabilities (
    (audio false)
    (code true)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (imageGeneration true)
    (imageOutput true)
    (local true)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 256000)
    (maxOutputTokens 32000)
  ))
  (pricing ())
  (properties (
    (id copilot/kimi-k2.7-code)
    (name "Kimi K2.7 Code")
    (capabilities (
      (family kimi-k2.7-code)
      (limits (
        (max_context_window_tokens 256000)
        (max_output_tokens 32000)
        (max_prompt_tokens 224000)
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
        (streaming true)
        (structured_outputs true)
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
        (inputPrice 95)
        (outputPrice 400)
        (cachePrice 19)
        (cacheReadPrice 19)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 224000)
        (maxPromptTokens 224000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to Kimi-K2.7-Code from Moonshot AI.")
    ))
    (quality_rank 21)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · Kimi K2.7 Code")
    (description "Authenticated GitHub Copilot backing model 'kimi-k2.7-code'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 256000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model kimi-k2.7-code)
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
        (enabled true)
        (status model_name_implied)
      ))
      (image_generation (
        (enabled true)
        (status tool_generated)
      ))
      (image_output (
        (enabled true)
        (status tool_generated)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled true)
        (capability image_output)
        (status tool_generated)
        (media_types ([]
          image/png
        ))
      ))
    ))
    (backingModelMetadata (
      (id kimi-k2.7-code)
      (name "Kimi K2.7 Code")
      (capabilities (
        (family kimi-k2.7-code)
        (limits (
          (max_context_window_tokens 256000)
          (max_output_tokens 32000)
          (max_prompt_tokens 224000)
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
          (streaming true)
          (structured_outputs true)
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
          (inputPrice 95)
          (outputPrice 400)
          (cachePrice 19)
          (cacheReadPrice 19)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 224000)
          (maxPromptTokens 224000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to Kimi-K2.7-Code from Moonshot AI.")
      ))
      (quality_rank 21)
      (quality_tier lightweight)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/kimi-k2.7-code)
    (name "Kimi K2.7 Code")
    (capabilities (
      (family kimi-k2.7-code)
      (limits (
        (max_context_window_tokens 256000)
        (max_output_tokens 32000)
        (max_prompt_tokens 224000)
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
        (streaming true)
        (structured_outputs true)
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
        (inputPrice 95)
        (outputPrice 400)
        (cachePrice 19)
        (cacheReadPrice 19)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 224000)
        (maxPromptTokens 224000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to Kimi-K2.7-Code from Moonshot AI.")
    ))
    (quality_rank 21)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · Kimi K2.7 Code")
    (description "Authenticated GitHub Copilot backing model 'kimi-k2.7-code'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 256000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model kimi-k2.7-code)
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
        (enabled true)
        (status model_name_implied)
      ))
      (image_generation (
        (enabled true)
        (status tool_generated)
      ))
      (image_output (
        (enabled true)
        (status tool_generated)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled true)
        (capability image_output)
        (status tool_generated)
        (media_types ([]
          image/png
        ))
      ))
    ))
    (backingModelMetadata (
      (id kimi-k2.7-code)
      (name "Kimi K2.7 Code")
      (capabilities (
        (family kimi-k2.7-code)
        (limits (
          (max_context_window_tokens 256000)
          (max_output_tokens 32000)
          (max_prompt_tokens 224000)
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
          (streaming true)
          (structured_outputs true)
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
          (inputPrice 95)
          (outputPrice 400)
          (cachePrice 19)
          (cacheReadPrice 19)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 224000)
          (maxPromptTokens 224000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to Kimi-K2.7-Code from Moonshot AI.")
      ))
      (quality_rank 21)
      (quality_tier lightweight)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/kimi-k2.7-code)
  ))
)
