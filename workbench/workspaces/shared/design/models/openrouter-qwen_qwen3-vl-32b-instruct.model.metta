({}
  (kind model)
  (id openrouter-qwen_qwen3-vl-32b-instruct)
  (label "Qwen: Qwen3 VL 32B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-32b-instruct)
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
    (contextWindow 131072)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.000000104")
    (completion "0.000000416")
  ))
  (properties ({}
    (id qwen/qwen3-vl-32b-instruct)
    (canonical_slug qwen/qwen3-vl-32b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-32B-Instruct)
    (name "Qwen: Qwen3 VL 32B Instruct")
    (created 1761231332)
    (description "Qwen3-VL-32B-Instruct is a large-scale multimodal vision-language model designed for high-precision understanding and reasoning across text, images, and video. With 32 billion parameters, it combines deep visual perception with advanced text...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000104")
      (completion "0.000000416")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
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
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-32b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-vl-32b-instruct)
    (canonical_slug qwen/qwen3-vl-32b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-32B-Instruct)
    (name "Qwen: Qwen3 VL 32B Instruct")
    (created 1761231332)
    (description "Qwen3-VL-32B-Instruct is a large-scale multimodal vision-language model designed for high-precision understanding and reasoning across text, images, and video. With 32 billion parameters, it combines deep visual perception with advanced text...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000104")
      (completion "0.000000416")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
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
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-32b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-32b-instruct)
  ))
)
