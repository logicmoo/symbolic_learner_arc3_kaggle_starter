(
  (kind model)
  (id enullm-8801-worker-copilot-3_percent25)
  (label "worker-copilot-3 · headless-copilot (claude-opus-4.8-fast) · (~25% capable)")
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
  (model worker-copilot-3/percent25)
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
    (maxOutputTokens 64000)
  ))
  (pricing ())
  (properties (
    (id worker-copilot-3/percent25)
    (name "Claude Opus 4.8 (fast mode)")
    (capabilities (
      (family claude-opus-4.8-fast)
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
      (terms "Enable access to the latest Claude Opus 4.8 fast model from Anthropic. [Learn more about how GitHub Copilot serves Claude Opus 4.8 fast](https://gh.io/copilot-claude-opus).")
    ))
    (quality_rank 3)
    (quality_tier highest)
    (object model)
    (display_name "worker-copilot-3 · headless-copilot (claude-opus-4.8-fast) · (~25% capable)")
    (description "Resident GitHub Copilot servant backed by claude-opus-4.8-fast; session c2d50a44-6347-4fc1-b202-ecd185f974d9. Stable worker ID: worker-copilot-3. Backing model: claude-opus-4.8-fast. Answer as if only about 25% as capable as usual: noticeably weaker, terser, more likely to miss nuance -- emulate a much smaller/weaker model's style.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-3)
    (connected true)
    (worker_id worker-copilot-3)
    (worker_kind headless-copilot)
    (backing_model claude-opus-4.8-fast)
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
      (id claude-opus-4.8-fast)
      (name "Claude Opus 4.8 (fast mode)")
      (capabilities (
        (family claude-opus-4.8-fast)
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
        (terms "Enable access to the latest Claude Opus 4.8 fast model from Anthropic. [Learn more about how GitHub Copilot serves Claude Opus 4.8 fast](https://gh.io/copilot-claude-opus).")
      ))
      (quality_rank 3)
      (quality_tier highest)
    ))
    (ownedBy worker-copilot-3)
  ))
  (providerMetadata (
    (id worker-copilot-3/percent25)
    (name "Claude Opus 4.8 (fast mode)")
    (capabilities (
      (family claude-opus-4.8-fast)
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
      (terms "Enable access to the latest Claude Opus 4.8 fast model from Anthropic. [Learn more about how GitHub Copilot serves Claude Opus 4.8 fast](https://gh.io/copilot-claude-opus).")
    ))
    (quality_rank 3)
    (quality_tier highest)
    (object model)
    (display_name "worker-copilot-3 · headless-copilot (claude-opus-4.8-fast) · (~25% capable)")
    (description "Resident GitHub Copilot servant backed by claude-opus-4.8-fast; session c2d50a44-6347-4fc1-b202-ecd185f974d9. Stable worker ID: worker-copilot-3. Backing model: claude-opus-4.8-fast. Answer as if only about 25% as capable as usual: noticeably weaker, terser, more likely to miss nuance -- emulate a much smaller/weaker model's style.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-3)
    (connected true)
    (worker_id worker-copilot-3)
    (worker_kind headless-copilot)
    (backing_model claude-opus-4.8-fast)
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
      (id claude-opus-4.8-fast)
      (name "Claude Opus 4.8 (fast mode)")
      (capabilities (
        (family claude-opus-4.8-fast)
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
        (terms "Enable access to the latest Claude Opus 4.8 fast model from Anthropic. [Learn more about how GitHub Copilot serves Claude Opus 4.8 fast](https://gh.io/copilot-claude-opus).")
      ))
      (quality_rank 3)
      (quality_tier highest)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-3/percent25)
  ))
)
