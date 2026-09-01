(
  (kind model)
  (id enullm-8801-copilot_gpt-5.5)
  (label "GitHub Copilot · GPT-5.5")
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
  (model copilot/gpt-5.5)
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
    (contextWindow 1050000)
    (maxOutputTokens 128000)
  ))
  (pricing ())
  (properties (
    (id copilot/gpt-5.5)
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
    (display_name "GitHub Copilot · GPT-5.5")
    (description "Authenticated GitHub Copilot backing model 'gpt-5.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1050000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model gpt-5.5)
    (connected true)
    (active_workers ([]
      worker-copilot-4
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
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/gpt-5.5)
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
    (display_name "GitHub Copilot · GPT-5.5")
    (description "Authenticated GitHub Copilot backing model 'gpt-5.5'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 1050000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model gpt-5.5)
    (connected true)
    (active_workers ([]
      worker-copilot-4
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
    (remoteModelId copilot/gpt-5.5)
  ))
)
