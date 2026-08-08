({}
  (kind model)
  (id openrouter-qwen_qwen3-vl-8b-instruct)
  (label "Qwen: Qwen3 VL 8B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-8b-instruct)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.000000117")
    (completion "0.000000455")
  ))
  (properties ({}
    (id qwen/qwen3-vl-8b-instruct)
    (canonical_slug qwen/qwen3-vl-8b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-8B-Instruct)
    (name "Qwen: Qwen3 VL 8B Instruct")
    (created 1760463308)
    (description "Qwen3-VL-8B-Instruct is a multimodal vision-language model from the Qwen3-VL series, built for high-fidelity understanding and reasoning across text, images, and video. It features improved multimodal fusion with Interleaved-MRoPE for long-horizon...")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000117")
      (completion "0.000000455")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 0.7)
      (top_p 0.8)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-8b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-vl-8b-instruct)
    (canonical_slug qwen/qwen3-vl-8b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-8B-Instruct)
    (name "Qwen: Qwen3 VL 8B Instruct")
    (created 1760463308)
    (description "Qwen3-VL-8B-Instruct is a multimodal vision-language model from the Qwen3-VL series, built for high-fidelity understanding and reasoning across text, images, and video. It features improved multimodal fusion with Interleaved-MRoPE for long-horizon...")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000117")
      (completion "0.000000455")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 0.7)
      (top_p 0.8)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-8b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-8b-instruct)
  ))
)
