(
  (kind model)
  (id openrouter-openai_gpt-5.6-terra-pro_batch)
  (label "OpenAI: GPT-5.6 Terra Pro (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.6-terra-pro:batch)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
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
  (pricing (
    (prompt "0.000001")
    (completion "0.000006")
    (web_search "0.01")
    (input_cache_read "0.0000001")
    (overrides ([]
      (
        (min_prompt_tokens 272000)
        (prompt "0.000002")
        (completion "0.000009")
        (input_cache_read "0.0000002")
      )
    ))
  ))
  (properties (
    (id openai/gpt-5.6-terra-pro:batch)
    (canonical_slug openai/gpt-5.6-terra-pro-20260709)
    (hugging_face_id null)
    (name "OpenAI: GPT-5.6 Terra Pro (batch)")
    (created 1783590861)
    (description "GPT-5.6 Terra Pro is the same underlying model as [GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra), served with `reasoning.mode` set to `pro` for higher-quality responses on complex tasks.\n\nLearn more in OpenAI's docs: https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode")
    (context_length 1050000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000006")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.000002")
          (completion "0.000009")
          (input_cache_read "0.0000002")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2026-02-16)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.6-terra-pro-20260709/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        max
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.6-terra-pro:batch)
    (canonical_slug openai/gpt-5.6-terra-pro-20260709)
    (hugging_face_id null)
    (name "OpenAI: GPT-5.6 Terra Pro (batch)")
    (created 1783590861)
    (description "GPT-5.6 Terra Pro is the same underlying model as [GPT-5.6 Terra](https://openrouter.ai/openai/gpt-5.6-terra), served with `reasoning.mode` set to `pro` for higher-quality responses on complex tasks.\n\nLearn more in OpenAI's docs: https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode")
    (context_length 1050000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000006")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.000002")
          (completion "0.000009")
          (input_cache_read "0.0000002")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2026-02-16)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.6-terra-pro-20260709/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        max
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.6-terra-pro:batch)
  ))
)
