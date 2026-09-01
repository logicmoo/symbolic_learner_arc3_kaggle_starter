(
  (kind model)
  (id enullm-8801-copilot_gemini-3.5-flash)
  (label "GitHub Copilot · Gemini 3.5 Flash")
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
  (model copilot/gemini-3.5-flash)
  (enabled true)
  (capabilities (
    (audio true)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
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
    (id copilot/gemini-3.5-flash)
    (name "Gemini 3.5 Flash")
    (capabilities (
      (family gemini-3.5-flash)
      (limits (
        (max_context_window_tokens 1000000)
        (max_output_tokens 64000)
        (max_prompt_tokens 936000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 10)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/heic
            image/heif
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (max_thinking_budget 24000)
        (min_thinking_budget 256)
        (parallel_tool_calls true)
        (reasoning_effort ([]
          minimal
          low
          medium
          high
        ))
        (streaming true)
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
        (inputPrice 150)
        (outputPrice 900)
        (cachePrice 15)
        (cacheReadPrice 15)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 150)
          (outputPrice 900)
          (cachePrice 15)
          (cacheReadPrice 15)
          (cacheWritePrice 0)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Gemini 3.5 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.5 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
    ))
    (quality_rank 20)
    (quality_tier versatile)
    (object model)
    (display_name "GitHub Copilot · Gemini 3.5 Flash")
    (description "Authenticated GitHub Copilot backing model 'gemini-3.5-flash'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1000000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model gemini-3.5-flash)
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
          image/heic
          image/heif
          application/pdf
        ))
        (enabled true)
      ))
      (audio (
        (status family_implied)
        (source "native_model_family; Copilot SDK does not advertise audio")
        (media_types ([]))
        (transport_supported true)
        (enabled true)
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
      (id gemini-3.5-flash)
      (name "Gemini 3.5 Flash")
      (capabilities (
        (family gemini-3.5-flash)
        (limits (
          (max_context_window_tokens 1000000)
          (max_output_tokens 64000)
          (max_prompt_tokens 936000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 10)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/heic
              image/heif
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (max_thinking_budget 24000)
          (min_thinking_budget 256)
          (parallel_tool_calls true)
          (reasoning_effort ([]
            minimal
            low
            medium
            high
          ))
          (streaming true)
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
          (inputPrice 150)
          (outputPrice 900)
          (cachePrice 15)
          (cacheReadPrice 15)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 150)
            (outputPrice 900)
            (cachePrice 15)
            (cacheReadPrice 15)
            (cacheWritePrice 0)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Gemini 3.5 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.5 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
      ))
      (quality_rank 20)
      (quality_tier versatile)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/gemini-3.5-flash)
    (name "Gemini 3.5 Flash")
    (capabilities (
      (family gemini-3.5-flash)
      (limits (
        (max_context_window_tokens 1000000)
        (max_output_tokens 64000)
        (max_prompt_tokens 936000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 10)
          (supported_media_types ([]
            image/jpeg
            image/png
            image/webp
            image/heic
            image/heif
            application/pdf
          ))
        ))
      ))
      (object model_capabilities)
      (supports (
        (max_thinking_budget 24000)
        (min_thinking_budget 256)
        (parallel_tool_calls true)
        (reasoning_effort ([]
          minimal
          low
          medium
          high
        ))
        (streaming true)
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
        (inputPrice 150)
        (outputPrice 900)
        (cachePrice 15)
        (cacheReadPrice 15)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 150)
          (outputPrice 900)
          (cachePrice 15)
          (cacheReadPrice 15)
          (cacheWritePrice 0)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Gemini 3.5 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.5 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
    ))
    (quality_rank 20)
    (quality_tier versatile)
    (object model)
    (display_name "GitHub Copilot · Gemini 3.5 Flash")
    (description "Authenticated GitHub Copilot backing model 'gemini-3.5-flash'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1000000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model gemini-3.5-flash)
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
          image/heic
          image/heif
          application/pdf
        ))
        (enabled true)
      ))
      (audio (
        (status family_implied)
        (source "native_model_family; Copilot SDK does not advertise audio")
        (media_types ([]))
        (transport_supported true)
        (enabled true)
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
      (id gemini-3.5-flash)
      (name "Gemini 3.5 Flash")
      (capabilities (
        (family gemini-3.5-flash)
        (limits (
          (max_context_window_tokens 1000000)
          (max_output_tokens 64000)
          (max_prompt_tokens 936000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 10)
            (supported_media_types ([]
              image/jpeg
              image/png
              image/webp
              image/heic
              image/heif
              application/pdf
            ))
          ))
        ))
        (object model_capabilities)
        (supports (
          (max_thinking_budget 24000)
          (min_thinking_budget 256)
          (parallel_tool_calls true)
          (reasoning_effort ([]
            minimal
            low
            medium
            high
          ))
          (streaming true)
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
          (inputPrice 150)
          (outputPrice 900)
          (cachePrice 15)
          (cacheReadPrice 15)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 150)
            (outputPrice 900)
            (cachePrice 15)
            (cacheReadPrice 15)
            (cacheWritePrice 0)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Gemini 3.5 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.5 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
      ))
      (quality_rank 20)
      (quality_tier versatile)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/gemini-3.5-flash)
  ))
)
