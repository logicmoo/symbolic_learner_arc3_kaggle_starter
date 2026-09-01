(
  (kind model)
  (id enullm-8801-worker-copilot-5_percent75)
  (label "worker-copilot-5 · headless-copilot (gemini-3.7-flash) · (~75% capable)")
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
  (model worker-copilot-5/percent75)
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
    (id worker-copilot-5/percent75)
    (name "Gemini 3.7 Flash")
    (capabilities (
      (family gemini-3.7-flash)
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
        (parallel_tool_calls true)
        (reasoning_effort ([]
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
        (inputPrice 75)
        (outputPrice 375)
        (cachePrice 7)
        (cacheReadPrice 7)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 75)
          (outputPrice 375)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Gemini 3.7 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.7 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
    ))
    (quality_rank 15)
    (quality_tier versatile)
    (object model)
    (display_name "worker-copilot-5 · headless-copilot (gemini-3.7-flash) · (~75% capable)")
    (description "Resident GitHub Copilot servant backed by gemini-3.7-flash; session c8528de3-f3bf-4bf4-92e6-0db26ac97679. Stable worker ID: worker-copilot-5. Backing model: gemini-3.7-flash. Answer as if only about 75% as capable as usual: slightly less careful/thorough, occasional minor omissions.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-5)
    (connected true)
    (worker_id worker-copilot-5)
    (worker_kind headless-copilot)
    (backing_model gemini-3.7-flash)
    (simulated true)
    (backingModelMetadata (
      (id gemini-3.7-flash)
      (name "Gemini 3.7 Flash")
      (capabilities (
        (family gemini-3.7-flash)
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
          (parallel_tool_calls true)
          (reasoning_effort ([]
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
          (inputPrice 75)
          (outputPrice 375)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 75)
            (outputPrice 375)
            (cachePrice 7)
            (cacheReadPrice 7)
            (cacheWritePrice 0)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Gemini 3.7 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.7 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
      ))
      (quality_rank 15)
      (quality_tier versatile)
    ))
    (ownedBy worker-copilot-5)
  ))
  (providerMetadata (
    (id worker-copilot-5/percent75)
    (name "Gemini 3.7 Flash")
    (capabilities (
      (family gemini-3.7-flash)
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
        (parallel_tool_calls true)
        (reasoning_effort ([]
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
        (inputPrice 75)
        (outputPrice 375)
        (cachePrice 7)
        (cacheReadPrice 7)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 200000)
        (maxPromptTokens 200000)
        (longContext (
          (inputPrice 75)
          (outputPrice 375)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (contextMax 936000)
          (maxPromptTokens 936000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest Gemini 3.7 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.7 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
    ))
    (quality_rank 15)
    (quality_tier versatile)
    (object model)
    (display_name "worker-copilot-5 · headless-copilot (gemini-3.7-flash) · (~75% capable)")
    (description "Resident GitHub Copilot servant backed by gemini-3.7-flash; session c8528de3-f3bf-4bf4-92e6-0db26ac97679. Stable worker ID: worker-copilot-5. Backing model: gemini-3.7-flash. Answer as if only about 75% as capable as usual: slightly less careful/thorough, occasional minor omissions.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-5)
    (connected true)
    (worker_id worker-copilot-5)
    (worker_kind headless-copilot)
    (backing_model gemini-3.7-flash)
    (simulated true)
    (backingModelMetadata (
      (id gemini-3.7-flash)
      (name "Gemini 3.7 Flash")
      (capabilities (
        (family gemini-3.7-flash)
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
          (parallel_tool_calls true)
          (reasoning_effort ([]
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
          (inputPrice 75)
          (outputPrice 375)
          (cachePrice 7)
          (cacheReadPrice 7)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 200000)
          (maxPromptTokens 200000)
          (longContext (
            (inputPrice 75)
            (outputPrice 375)
            (cachePrice 7)
            (cacheReadPrice 7)
            (cacheWritePrice 0)
            (contextMax 936000)
            (maxPromptTokens 936000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest Gemini 3.7 Flash model from Google. [Learn more about how GitHub Copilot serves Gemini 3.7 Flash](https://docs.github.com/en/copilot/reference/ai-models/model-hosting#google-models).")
      ))
      (quality_rank 15)
      (quality_tier versatile)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-5/percent75)
  ))
)
