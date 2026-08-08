(
  (kind model)
  (id openrouter-google_gemini-3.1-pro-preview_batch)
  (label "Google: Gemini 3.1 Pro Preview (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.1-pro-preview:batch)
  (enabled true)
  (capabilities (
    (audio true)
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
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.000001")
    (completion "0.000006")
    (image "0.000001")
    (audio "0.000001")
    (web_search "0.014")
    (internal_reasoning "0.000006")
    (overrides ([]
      (
        (min_prompt_tokens 200000)
        (prompt "0.000002")
        (completion "0.000009")
        (audio "0.000002")
      )
    ))
  ))
  (properties (
    (id google/gemini-3.1-pro-preview:batch)
    (canonical_slug google/gemini-3.1-pro-preview-20260219)
    (hugging_face_id "")
    (name "Google: Gemini 3.1 Pro Preview (batch)")
    (created 1771509627)
    (description "Gemini 3.1 Pro Preview is Google’s frontier reasoning model, delivering enhanced software engineering performance, improved agentic reliability, and more efficient token usage across complex workflows. Building on the multimodal foundation...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        audio
        file
        image
        text
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000006")
      (image "0.000001")
      (audio "0.000001")
      (web_search "0.014")
      (internal_reasoning "0.000006")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000002")
          (completion "0.000009")
          (audio "0.000002")
        )
      ))
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.1-pro-preview-20260219/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1125)
          (win_rate 44.1)
          (rank 17)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1226)
          (win_rate 55.8)
          (rank 5)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1112)
          (win_rate 33.8)
          (rank 8)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1219)
          (win_rate 54.4)
          (rank 5)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1107)
          (win_rate 33.9)
          (rank 8)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1079)
          (win_rate 41.5)
          (rank 28)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1109)
          (win_rate 43)
          (rank 21)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1236)
          (win_rate 60)
          (rank 6)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1203)
          (win_rate 51.9)
          (rank 11)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1151)
          (win_rate 45.1)
          (rank 24)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1110)
          (win_rate 34.1)
          (rank 8)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1109)
          (win_rate 31.9)
          (rank 17)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1174)
          (win_rate 46.6)
          (rank 22)
        )
        (
          (arena models)
          (category 3d)
          (elo 1286)
          (win_rate 59.4)
          (rank 23)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1307)
          (win_rate 63.5)
          (rank 5)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1269)
          (win_rate 64.2)
          (rank 27)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1253)
          (win_rate 60.5)
          (rank 31)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1240)
          (win_rate 54)
          (rank 34)
        )
        (
          (arena models)
          (category svg)
          (elo 1334)
          (win_rate 68.8)
          (rank 2)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1300)
          (win_rate 68.1)
          (rank 15)
        )
        (
          (arena models)
          (category website)
          (elo 1273)
          (win_rate 64.3)
          (rank 24)
        )
      ))
      (artificial_analysis (
        (intelligence_index 47.7)
        (coding_index 68.8)
        (agentic_index 23)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-3.1-pro-preview:batch)
    (canonical_slug google/gemini-3.1-pro-preview-20260219)
    (hugging_face_id "")
    (name "Google: Gemini 3.1 Pro Preview (batch)")
    (created 1771509627)
    (description "Gemini 3.1 Pro Preview is Google’s frontier reasoning model, delivering enhanced software engineering performance, improved agentic reliability, and more efficient token usage across complex workflows. Building on the multimodal foundation...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        audio
        file
        image
        text
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000006")
      (image "0.000001")
      (audio "0.000001")
      (web_search "0.014")
      (internal_reasoning "0.000006")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000002")
          (completion "0.000009")
          (audio "0.000002")
        )
      ))
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.1-pro-preview-20260219/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1125)
          (win_rate 44.1)
          (rank 17)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1226)
          (win_rate 55.8)
          (rank 5)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1112)
          (win_rate 33.8)
          (rank 8)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1219)
          (win_rate 54.4)
          (rank 5)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1107)
          (win_rate 33.9)
          (rank 8)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1079)
          (win_rate 41.5)
          (rank 28)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1109)
          (win_rate 43)
          (rank 21)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1236)
          (win_rate 60)
          (rank 6)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1203)
          (win_rate 51.9)
          (rank 11)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1151)
          (win_rate 45.1)
          (rank 24)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1110)
          (win_rate 34.1)
          (rank 8)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1109)
          (win_rate 31.9)
          (rank 17)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1174)
          (win_rate 46.6)
          (rank 22)
        )
        (
          (arena models)
          (category 3d)
          (elo 1286)
          (win_rate 59.4)
          (rank 23)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1307)
          (win_rate 63.5)
          (rank 5)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1269)
          (win_rate 64.2)
          (rank 27)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1253)
          (win_rate 60.5)
          (rank 31)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1240)
          (win_rate 54)
          (rank 34)
        )
        (
          (arena models)
          (category svg)
          (elo 1334)
          (win_rate 68.8)
          (rank 2)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1300)
          (win_rate 68.1)
          (rank 15)
        )
        (
          (arena models)
          (category website)
          (elo 1273)
          (win_rate 64.3)
          (rank 24)
        )
      ))
      (artificial_analysis (
        (intelligence_index 47.7)
        (coding_index 68.8)
        (agentic_index 23)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.1-pro-preview:batch)
  ))
)
