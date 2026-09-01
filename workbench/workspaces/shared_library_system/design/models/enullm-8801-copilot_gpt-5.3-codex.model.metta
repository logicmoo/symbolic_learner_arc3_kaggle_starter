(
  (kind model)
  (id enullm-8801-copilot_gpt-5.3-codex)
  (label "GitHub Copilot · GPT-5.3-Codex")
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
  (model copilot/gpt-5.3-codex)
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
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing ())
  (properties (
    (id copilot/gpt-5.3-codex)
    (name GPT-5.3-Codex)
    (capabilities (
      (family gpt-5.3-codex)
      (limits (
        (max_context_window_tokens 400000)
        (max_output_tokens 128000)
        (max_prompt_tokens 272000)
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
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          medium
          high
          xhigh
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
        (inputPrice 175)
        (outputPrice 1400)
        (cachePrice 17)
        (cacheReadPrice 17)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
      ))
    ))
    (quality_rank 12)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · GPT-5.3-Codex")
    (description "Authenticated GitHub Copilot backing model 'gpt-5.3-codex'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 400000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier copilot)
    (backing_model gpt-5.3-codex)
    (connected true)
    (active_workers ([]
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (policy ())
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
      (id gpt-5.3-codex)
      (name GPT-5.3-Codex)
      (capabilities (
        (family gpt-5.3-codex)
        (limits (
          (max_context_window_tokens 400000)
          (max_output_tokens 128000)
          (max_prompt_tokens 272000)
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
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            medium
            high
            xhigh
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
          (inputPrice 175)
          (outputPrice 1400)
          (cachePrice 17)
          (cacheReadPrice 17)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
        ))
      ))
      (quality_rank 12)
      (quality_tier powerful)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/gpt-5.3-codex)
    (name GPT-5.3-Codex)
    (capabilities (
      (family gpt-5.3-codex)
      (limits (
        (max_context_window_tokens 400000)
        (max_output_tokens 128000)
        (max_prompt_tokens 272000)
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
        (parallel_tool_calls true)
        (reasoning_effort ([]
          low
          medium
          high
          xhigh
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
        (inputPrice 175)
        (outputPrice 1400)
        (cachePrice 17)
        (cacheReadPrice 17)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
      ))
    ))
    (quality_rank 12)
    (quality_tier powerful)
    (object model)
    (display_name "GitHub Copilot · GPT-5.3-Codex")
    (description "Authenticated GitHub Copilot backing model 'gpt-5.3-codex'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 400000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier copilot)
    (backing_model gpt-5.3-codex)
    (connected true)
    (active_workers ([]
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (policy ())
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
      (id gpt-5.3-codex)
      (name GPT-5.3-Codex)
      (capabilities (
        (family gpt-5.3-codex)
        (limits (
          (max_context_window_tokens 400000)
          (max_output_tokens 128000)
          (max_prompt_tokens 272000)
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
          (parallel_tool_calls true)
          (reasoning_effort ([]
            low
            medium
            high
            xhigh
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
          (inputPrice 175)
          (outputPrice 1400)
          (cachePrice 17)
          (cacheReadPrice 17)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
        ))
      ))
      (quality_rank 12)
      (quality_tier powerful)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/gpt-5.3-codex)
  ))
)
