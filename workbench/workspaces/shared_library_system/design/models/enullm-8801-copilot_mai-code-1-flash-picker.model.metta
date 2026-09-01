(
  (kind model)
  (id enullm-8801-copilot_mai-code-1-flash-picker)
  (label "GitHub Copilot · MAI-Code-1-Flash")
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
  (model copilot/mai-code-1-flash-picker)
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
    (vision false)
  ))
  (limits (
    (contextWindow 256000)
    (maxOutputTokens 128000)
  ))
  (pricing ())
  (properties (
    (id copilot/mai-code-1-flash-picker)
    (name MAI-Code-1-Flash)
    (capabilities (
      (family oswe-vscode-modelD)
      (limits (
        (max_context_window_tokens 256000)
        (max_output_tokens 128000)
        (max_prompt_tokens 128000)
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
        (contextMax 128000)
        (maxPromptTokens 128000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "")
    ))
    (quality_rank 26)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · MAI-Code-1-Flash")
    (description "Authenticated GitHub Copilot backing model 'mai-code-1-flash-picker'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 256000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model mai-code-1-flash-picker)
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
        (status not_advertised)
        (media_types ([]))
        (enabled false)
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
      (id mai-code-1-flash-picker)
      (name MAI-Code-1-Flash)
      (capabilities (
        (family oswe-vscode-modelD)
        (limits (
          (max_context_window_tokens 256000)
          (max_output_tokens 128000)
          (max_prompt_tokens 128000)
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
          (contextMax 128000)
          (maxPromptTokens 128000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "")
      ))
      (quality_rank 26)
      (quality_tier lightweight)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/mai-code-1-flash-picker)
    (name MAI-Code-1-Flash)
    (capabilities (
      (family oswe-vscode-modelD)
      (limits (
        (max_context_window_tokens 256000)
        (max_output_tokens 128000)
        (max_prompt_tokens 128000)
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
        (contextMax 128000)
        (maxPromptTokens 128000)
      ))
    ))
    (policy (
      (state enabled)
      (terms "")
    ))
    (quality_rank 26)
    (quality_tier lightweight)
    (object model)
    (display_name "GitHub Copilot · MAI-Code-1-Flash")
    (description "Authenticated GitHub Copilot backing model 'mai-code-1-flash-picker'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 256000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (codex_supplier null)
    (backing_model mai-code-1-flash-picker)
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
        (status not_advertised)
        (media_types ([]))
        (enabled false)
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
      (id mai-code-1-flash-picker)
      (name MAI-Code-1-Flash)
      (capabilities (
        (family oswe-vscode-modelD)
        (limits (
          (max_context_window_tokens 256000)
          (max_output_tokens 128000)
          (max_prompt_tokens 128000)
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
          (contextMax 128000)
          (maxPromptTokens 128000)
        ))
      ))
      (policy (
        (state enabled)
        (terms "")
      ))
      (quality_rank 26)
      (quality_tier lightweight)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/mai-code-1-flash-picker)
  ))
)
