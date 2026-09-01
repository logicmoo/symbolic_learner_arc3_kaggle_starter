(
  (kind model)
  (id enullm-8801-worker-copilot-1_gpt-5.4-mini)
  (label "worker-copilot-1 · headless-copilot backed by GPT-5.4 mini (gpt-5.4-mini)")
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
  (model worker-copilot-1/gpt-5.4-mini)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing ())
  (properties (
    (id worker-copilot-1/gpt-5.4-mini)
    (name "GPT-5.4 mini")
    (capabilities (
      (family gpt-5.4-mini)
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
          none
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
        (inputPrice 75)
        (outputPrice 450)
        (cachePrice 7)
        (cacheReadPrice 7)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest GPT-5.4 mini model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.4 mini](https://gh.io/copilot-openai).")
    ))
    (quality_rank 22)
    (quality_tier lightweight)
    (object model)
    (display_name "worker-copilot-1 · headless-copilot backed by GPT-5.4 mini (gpt-5.4-mini)")
    (description "Direct alias for stable worker 'worker-copilot-1' using its active backing model 'gpt-5.4-mini'.")
    (context_length 400000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by worker-copilot-1)
    (connected true)
    (worker_id worker-copilot-1)
    (worker_kind headless-copilot)
    (backing_model gpt-5.4-mini)
    (simulated true)
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
    (backingModelMetadata (
      (id gpt-5.4-mini)
      (name "GPT-5.4 mini")
      (capabilities (
        (family gpt-5.4-mini)
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
            none
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
          (inputPrice 75)
          (outputPrice 450)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest GPT-5.4 mini model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.4 mini](https://gh.io/copilot-openai).")
      ))
      (quality_rank 22)
      (quality_tier lightweight)
    ))
    (ownedBy worker-copilot-1)
  ))
  (providerMetadata (
    (id worker-copilot-1/gpt-5.4-mini)
    (name "GPT-5.4 mini")
    (capabilities (
      (family gpt-5.4-mini)
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
          none
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
        (inputPrice 75)
        (outputPrice 450)
        (cachePrice 7)
        (cacheReadPrice 7)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest GPT-5.4 mini model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.4 mini](https://gh.io/copilot-openai).")
    ))
    (quality_rank 22)
    (quality_tier lightweight)
    (object model)
    (display_name "worker-copilot-1 · headless-copilot backed by GPT-5.4 mini (gpt-5.4-mini)")
    (description "Direct alias for stable worker 'worker-copilot-1' using its active backing model 'gpt-5.4-mini'.")
    (context_length 400000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by worker-copilot-1)
    (connected true)
    (worker_id worker-copilot-1)
    (worker_kind headless-copilot)
    (backing_model gpt-5.4-mini)
    (simulated true)
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
    (backingModelMetadata (
      (id gpt-5.4-mini)
      (name "GPT-5.4 mini")
      (capabilities (
        (family gpt-5.4-mini)
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
            none
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
          (inputPrice 75)
          (outputPrice 450)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest GPT-5.4 mini model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.4 mini](https://gh.io/copilot-openai).")
      ))
      (quality_rank 22)
      (quality_tier lightweight)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-1/gpt-5.4-mini)
  ))
)
