(
  (kind model)
  (id enullm-8801-worker-copilot-2_percent100)
  (label "worker-copilot-2 · headless-copilot (grok-4.5) · (100% -- normal)")
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
  (model worker-copilot-2/percent100)
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
    (contextWindow 200000)
    (maxOutputTokens 128000)
  ))
  (pricing ())
  (properties (
    (id worker-copilot-2/percent100)
    (name "Grok 4.5")
    (capabilities (
      (family grok-4.5)
      (limits (
        (max_context_window_tokens 500000)
        (max_output_tokens 128000)
        (max_prompt_tokens 372000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
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
        (inputPrice 200)
        (outputPrice 600)
        (cachePrice 50)
        (cacheReadPrice 50)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 400)
          (outputPrice 1200)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 0)
          (contextMax 500000)
          (maxPromptTokens 500000)
        ))
      ))
    ))
    (quality_rank 16)
    (quality_tier versatile)
    (object model)
    (display_name "worker-copilot-2 · headless-copilot (grok-4.5) · (100% -- normal)")
    (description "Resident GitHub Copilot servant backed by grok-4.5; session 45f79464-c8d3-4525-ba27-1d1d1e374d43. Stable worker ID: worker-copilot-2. Backing model: grok-4.5. Answer normally, at your full/actual capability.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-2)
    (connected true)
    (worker_id worker-copilot-2)
    (worker_kind headless-copilot)
    (backing_model grok-4.5)
    (simulated true)
    (on_demand false)
    (input_modalities (
      (image (
        (enabled false)
      ))
      (audio (
        (enabled false)
      ))
      (general_file (
        (enabled false)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
      ))
      (summarization (
        (enabled false)
      ))
    ))
    (backingModelMetadata (
      (id grok-4.5)
      (name "Grok 4.5")
      (capabilities (
        (family grok-4.5)
        (limits (
          (max_context_window_tokens 500000)
          (max_output_tokens 128000)
          (max_prompt_tokens 372000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
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
          (inputPrice 200)
          (outputPrice 600)
          (cachePrice 50)
          (cacheReadPrice 50)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 400)
            (outputPrice 1200)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 0)
            (contextMax 500000)
            (maxPromptTokens 500000)
          ))
        ))
      ))
      (quality_rank 16)
      (quality_tier versatile)
    ))
    (ownedBy worker-copilot-2)
  ))
  (providerMetadata (
    (id worker-copilot-2/percent100)
    (name "Grok 4.5")
    (capabilities (
      (family grok-4.5)
      (limits (
        (max_context_window_tokens 500000)
        (max_output_tokens 128000)
        (max_prompt_tokens 372000)
        (vision (
          (max_prompt_image_size 3145728)
          (max_prompt_images 1)
          (supported_media_types ([]
            image/jpeg
            image/png
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
        (inputPrice 200)
        (outputPrice 600)
        (cachePrice 50)
        (cacheReadPrice 50)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 400)
          (outputPrice 1200)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 0)
          (contextMax 500000)
          (maxPromptTokens 500000)
        ))
      ))
    ))
    (quality_rank 16)
    (quality_tier versatile)
    (object model)
    (display_name "worker-copilot-2 · headless-copilot (grok-4.5) · (100% -- normal)")
    (description "Resident GitHub Copilot servant backed by grok-4.5; session 45f79464-c8d3-4525-ba27-1d1d1e374d43. Stable worker ID: worker-copilot-2. Backing model: grok-4.5. Answer normally, at your full/actual capability.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-2)
    (connected true)
    (worker_id worker-copilot-2)
    (worker_kind headless-copilot)
    (backing_model grok-4.5)
    (simulated true)
    (on_demand false)
    (input_modalities (
      (image (
        (enabled false)
      ))
      (audio (
        (enabled false)
      ))
      (general_file (
        (enabled false)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
      ))
      (summarization (
        (enabled false)
      ))
    ))
    (backingModelMetadata (
      (id grok-4.5)
      (name "Grok 4.5")
      (capabilities (
        (family grok-4.5)
        (limits (
          (max_context_window_tokens 500000)
          (max_output_tokens 128000)
          (max_prompt_tokens 372000)
          (vision (
            (max_prompt_image_size 3145728)
            (max_prompt_images 1)
            (supported_media_types ([]
              image/jpeg
              image/png
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
          (inputPrice 200)
          (outputPrice 600)
          (cachePrice 50)
          (cacheReadPrice 50)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 400)
            (outputPrice 1200)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 0)
            (contextMax 500000)
            (maxPromptTokens 500000)
          ))
        ))
      ))
      (quality_rank 16)
      (quality_tier versatile)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-2/percent100)
  ))
)
