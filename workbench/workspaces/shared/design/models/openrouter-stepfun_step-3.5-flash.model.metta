({}
  (kind model)
  (id openrouter-stepfun_step-3.5-flash)
  (label "StepFun: Step 3.5 Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model stepfun/step-3.5-flash)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.0000001")
    (completion "0.0000003")
  ))
  (properties ({}
    (id stepfun/step-3.5-flash)
    (canonical_slug stepfun/step-3.5-flash)
    (hugging_face_id stepfun-ai/Step-3.5-Flash)
    (name "StepFun: Step 3.5 Flash")
    (created 1769728337)
    (description "Step 3.5 Flash is StepFun's most capable open-source foundation model. Built on a sparse Mixture of Experts (MoE) architecture, it selectively activates only 11B of its 196B parameters per token....")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000001")
      (completion "0.0000003")
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
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/stepfun/step-3.5-flash/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id stepfun/step-3.5-flash)
    (canonical_slug stepfun/step-3.5-flash)
    (hugging_face_id stepfun-ai/Step-3.5-Flash)
    (name "StepFun: Step 3.5 Flash")
    (created 1769728337)
    (description "Step 3.5 Flash is StepFun's most capable open-source foundation model. Built on a sparse Mixture of Experts (MoE) architecture, it selectively activates only 11B of its 196B parameters per token....")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000001")
      (completion "0.0000003")
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
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/stepfun/step-3.5-flash/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId stepfun/step-3.5-flash)
  ))
)
