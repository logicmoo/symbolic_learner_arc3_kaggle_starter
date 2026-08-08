({}
  (kind model)
  (id openrouter-qwen_qwen3.5-397b-a17b)
  (label "Qwen: Qwen3.5 397B A17B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.5-397b-a17b)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.00000039")
    (completion "0.00000234")
  ))
  (properties ({}
    (id qwen/qwen3.5-397b-a17b)
    (canonical_slug qwen/qwen3.5-397b-a17b-20260216)
    (hugging_face_id Qwen/Qwen3.5-397B-A17B)
    (name "Qwen: Qwen3.5 397B A17B")
    (created 1771223018)
    (description "The Qwen3.5 series 397B-A17B native vision-language model is built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. It delivers...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000039")
      (completion "0.00000234")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
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
      (temperature 0.6)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.5-397b-a17b-20260216/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1215)
          (win_rate 56.7)
          (rank 43)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1208)
          (win_rate 52.6)
          (rank 45)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1203)
          (win_rate 53.2)
          (rank 46)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1181)
          (win_rate 50.1)
          (rank 55)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1188)
          (win_rate 56.1)
          (rank 35)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1196)
          (win_rate 51.4)
          (rank 55)
        )
        ({}
          (arena models)
          (category website)
          (elo 1213)
          (win_rate 52.6)
          (rank 47)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 34.3)
        (coding_index 48.2)
        (agentic_index 19.8)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3.5-397b-a17b)
    (canonical_slug qwen/qwen3.5-397b-a17b-20260216)
    (hugging_face_id Qwen/Qwen3.5-397B-A17B)
    (name "Qwen: Qwen3.5 397B A17B")
    (created 1771223018)
    (description "The Qwen3.5 series 397B-A17B native vision-language model is built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. It delivers...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000039")
      (completion "0.00000234")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
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
      (temperature 0.6)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.5-397b-a17b-20260216/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1215)
          (win_rate 56.7)
          (rank 43)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1208)
          (win_rate 52.6)
          (rank 45)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1203)
          (win_rate 53.2)
          (rank 46)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1181)
          (win_rate 50.1)
          (rank 55)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1188)
          (win_rate 56.1)
          (rank 35)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1196)
          (win_rate 51.4)
          (rank 55)
        )
        ({}
          (arena models)
          (category website)
          (elo 1213)
          (win_rate 52.6)
          (rank 47)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 34.3)
        (coding_index 48.2)
        (agentic_index 19.8)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.5-397b-a17b)
  ))
)
