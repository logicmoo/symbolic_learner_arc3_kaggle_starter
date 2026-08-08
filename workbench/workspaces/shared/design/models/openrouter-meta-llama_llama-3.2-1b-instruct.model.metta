({}
  (kind model)
  (id openrouter-meta-llama_llama-3.2-1b-instruct)
  (label "Meta: Llama 3.2 1B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-3.2-1b-instruct)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits ({}
    (contextWindow 60000)
    (maxOutputTokens 60000)
  ))
  (pricing ({}
    (prompt "0.000000027")
    (completion "0.000000201")
  ))
  (properties ({}
    (id meta-llama/llama-3.2-1b-instruct)
    (canonical_slug meta-llama/llama-3.2-1b-instruct)
    (hugging_face_id meta-llama/Llama-3.2-1B-Instruct)
    (name "Meta: Llama 3.2 1B Instruct")
    (created 1727222400)
    (description "Llama 3.2 1B is a 1-billion-parameter language model focused on efficiently performing natural language tasks, such as summarization, dialogue, and multilingual text analysis. Its smaller size allows it to operate...")
    (context_length 60000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing ({}
      (prompt "0.000000027")
      (completion "0.000000201")
    ))
    (top_provider ({}
      (context_length 60000)
      (max_completion_tokens 60000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-3.2-1b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id meta-llama/llama-3.2-1b-instruct)
    (canonical_slug meta-llama/llama-3.2-1b-instruct)
    (hugging_face_id meta-llama/Llama-3.2-1B-Instruct)
    (name "Meta: Llama 3.2 1B Instruct")
    (created 1727222400)
    (description "Llama 3.2 1B is a 1-billion-parameter language model focused on efficiently performing natural language tasks, such as summarization, dialogue, and multilingual text analysis. Its smaller size allows it to operate...")
    (context_length 60000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing ({}
      (prompt "0.000000027")
      (completion "0.000000201")
    ))
    (top_provider ({}
      (context_length 60000)
      (max_completion_tokens 60000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-3.2-1b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-3.2-1b-instruct)
  ))
)
