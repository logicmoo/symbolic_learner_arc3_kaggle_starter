(
  (kind model)
  (id enullm-8801-worker-copilot-4_percent75)
  (label "worker-copilot-4 · headless-copilot (gpt-5.5) · (~75% capable)")
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
  (model worker-copilot-4/percent75)
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
    (id worker-copilot-4/percent75)
    (name GPT-5.5)
    (capabilities (
      (family gpt-5.5)
      (limits (
        (max_context_window_tokens 1050000)
        (max_output_tokens 128000)
        (max_prompt_tokens 922000)
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
        (inputPrice 500)
        (outputPrice 3000)
        (cachePrice 50)
        (cacheReadPrice 50)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
        (longContext (
          (inputPrice 1000)
          (outputPrice 4500)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 0)
          (contextMax 922000)
          (maxPromptTokens 922000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest GPT-5.5 model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.5](https://gh.io/copilot-openai).")
    ))
    (quality_rank 5)
    (quality_tier highest)
    (object model)
    (display_name "worker-copilot-4 · headless-copilot (gpt-5.5) · (~75% capable)")
    (description "Resident GitHub Copilot servant backed by gpt-5.5; session ad288b0b-fbcb-4542-b166-ba16d2a0aeaf. Stable worker ID: worker-copilot-4. Backing model: gpt-5.5. Answer as if only about 75% as capable as usual: slightly less careful/thorough, occasional minor omissions.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-4)
    (connected true)
    (worker_id worker-copilot-4)
    (worker_kind headless-copilot)
    (backing_model gpt-5.5)
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
      (id gpt-5.5)
      (name GPT-5.5)
      (capabilities (
        (family gpt-5.5)
        (limits (
          (max_context_window_tokens 1050000)
          (max_output_tokens 128000)
          (max_prompt_tokens 922000)
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
          (inputPrice 500)
          (outputPrice 3000)
          (cachePrice 50)
          (cacheReadPrice 50)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
          (longContext (
            (inputPrice 1000)
            (outputPrice 4500)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 0)
            (contextMax 922000)
            (maxPromptTokens 922000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest GPT-5.5 model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.5](https://gh.io/copilot-openai).")
      ))
      (quality_rank 5)
      (quality_tier highest)
    ))
    (ownedBy worker-copilot-4)
  ))
  (providerMetadata (
    (id worker-copilot-4/percent75)
    (name GPT-5.5)
    (capabilities (
      (family gpt-5.5)
      (limits (
        (max_context_window_tokens 1050000)
        (max_output_tokens 128000)
        (max_prompt_tokens 922000)
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
        (inputPrice 500)
        (outputPrice 3000)
        (cachePrice 50)
        (cacheReadPrice 50)
        (cacheWritePrice 0)
        (batchSize 1000000)
        (contextMax 272000)
        (maxPromptTokens 272000)
        (longContext (
          (inputPrice 1000)
          (outputPrice 4500)
          (cachePrice 100)
          (cacheReadPrice 100)
          (cacheWritePrice 0)
          (contextMax 922000)
          (maxPromptTokens 922000)
        ))
      ))
    ))
    (policy (
      (state enabled)
      (terms "Enable access to the latest GPT-5.5 model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.5](https://gh.io/copilot-openai).")
    ))
    (quality_rank 5)
    (quality_tier highest)
    (object model)
    (display_name "worker-copilot-4 · headless-copilot (gpt-5.5) · (~75% capable)")
    (description "Resident GitHub Copilot servant backed by gpt-5.5; session ad288b0b-fbcb-4542-b166-ba16d2a0aeaf. Stable worker ID: worker-copilot-4. Backing model: gpt-5.5. Answer as if only about 75% as capable as usual: slightly less careful/thorough, occasional minor omissions.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-4)
    (connected true)
    (worker_id worker-copilot-4)
    (worker_kind headless-copilot)
    (backing_model gpt-5.5)
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
      (id gpt-5.5)
      (name GPT-5.5)
      (capabilities (
        (family gpt-5.5)
        (limits (
          (max_context_window_tokens 1050000)
          (max_output_tokens 128000)
          (max_prompt_tokens 922000)
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
          (inputPrice 500)
          (outputPrice 3000)
          (cachePrice 50)
          (cacheReadPrice 50)
          (cacheWritePrice 0)
          (batchSize 1000000)
          (contextMax 272000)
          (maxPromptTokens 272000)
          (longContext (
            (inputPrice 1000)
            (outputPrice 4500)
            (cachePrice 100)
            (cacheReadPrice 100)
            (cacheWritePrice 0)
            (contextMax 922000)
            (maxPromptTokens 922000)
          ))
        ))
      ))
      (policy (
        (state enabled)
        (terms "Enable access to the latest GPT-5.5 model from OpenAI. [Learn more about how GitHub Copilot serves GPT-5.5](https://gh.io/copilot-openai).")
      ))
      (quality_rank 5)
      (quality_tier highest)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId worker-copilot-4/percent75)
  ))
)
