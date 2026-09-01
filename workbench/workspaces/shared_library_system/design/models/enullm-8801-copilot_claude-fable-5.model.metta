(
  (kind model)
  (id enullm-8801-copilot_claude-fable-5)
  (label "GitHub Copilot · Claude Fable 5")
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
  (model copilot/claude-fable-5)
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
    (contextWindow 1000000)
    (maxOutputTokens 64000)
  ))
  (pricing ())
  (properties (
    (id copilot/claude-fable-5)
    (name "Claude Fable 5")
    (capabilities (
      (family claude-fable-5)
      (limits (
        (max_context_window_tokens 1000000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 64000)
        (max_prompt_tokens 936000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/gif
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (adaptive_thinking required)
        (max_thinking_budget 32000)
        (min_thinking_budget 1024)
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          medium
          high
          xhigh
          max
        ))
        (streaming true)
        (structured_outputs true)
        (tool_calls true)
        (vision true)
        (reasoningEffort true)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 1000)
        (outputPrice 5000)
        (cachePrice 100)
        (cacheReadPrice 100)
        (cacheWritePrice 1250)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 1000)
          (outputPrice 5000)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 1250)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Fable 5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Fable 5](https://gh.io/copilot-claude-opus).")
    ))
    (quality_rank 13)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · Claude Fable 5")
    (description "Authenticated GitHub Copilot backing model 'claude-fable-5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1000000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model claude-fable-5)
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
      (id claude-fable-5)
      (name "Claude Fable 5")
      (capabilities (
        (family claude-fable-5)
        (limits (
          (max_context_window_tokens 1000000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 64000)
          (max_prompt_tokens 936000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/gif
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (adaptive_thinking required)
          (max_thinking_budget 32000)
          (min_thinking_budget 1024)
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            medium
            high
            xhigh
            max
          ))
          (streaming true)
          (structured_outputs true)
          (tool_calls true)
          (vision true)
          (reasoningEffort true)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 1000)
          (outputPrice 5000)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 1250)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 1000)
            (outputPrice 5000)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 1250)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Fable 5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Fable 5](https://gh.io/copilot-claude-opus).")
      ))
      (quality_rank 13)
      (quality_tier powerful)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/claude-fable-5)
    (name "Claude Fable 5")
    (capabilities (
      (family claude-fable-5)
      (limits (
        (max_context_window_tokens 1000000)
        (max_non_streaming_output_tokens 16000)
        (max_output_tokens 64000)
        (max_prompt_tokens 936000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/gif
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (adaptive_thinking required)
        (max_thinking_budget 32000)
        (min_thinking_budget 1024)
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          medium
          high
          xhigh
          max
        ))
        (streaming true)
        (structured_outputs true)
        (tool_calls true)
        (vision true)
        (reasoningEffort true)
      ))
      (tokenizer o200k_base)
      (type chat)
    ))
    (billing (
      (tokenPrices (
        (inputPrice 1000)
        (outputPrice 5000)
        (cachePrice 100)
        (cacheReadPrice 100)
        (cacheWritePrice 1250)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 1000)
          (outputPrice 5000)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 1250)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Claude Fable 5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Fable 5](https://gh.io/copilot-claude-opus).")
    ))
    (quality_rank 13)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · Claude Fable 5")
    (description "Authenticated GitHub Copilot backing model 'claude-fable-5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1000000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model claude-fable-5)
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
      (id claude-fable-5)
      (name "Claude Fable 5")
      (capabilities (
        (family claude-fable-5)
        (limits (
          (max_context_window_tokens 1000000)
          (max_non_streaming_output_tokens 16000)
          (max_output_tokens 64000)
          (max_prompt_tokens 936000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/gif
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (adaptive_thinking required)
          (max_thinking_budget 32000)
          (min_thinking_budget 1024)
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            medium
            high
            xhigh
            max
          ))
          (streaming true)
          (structured_outputs true)
          (tool_calls true)
          (vision true)
          (reasoningEffort true)
        ))
        (tokenizer o200k_base)
        (type chat)
      ))
      (billing (
        (tokenPrices (
          (inputPrice 1000)
          (outputPrice 5000)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 1250)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 1000)
            (outputPrice 5000)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 1250)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Claude Fable 5 model from Anthropic. [Learn more about how GitHub Copilot serves Claude Fable 5](https://gh.io/copilot-claude-opus).")
      ))
      (quality_rank 13)
      (quality_tier powerful)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/claude-fable-5)
  ))
)
