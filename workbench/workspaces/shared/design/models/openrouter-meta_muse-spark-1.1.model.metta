(
  (kind model)
  (id openrouter-meta_muse-spark-1.1)
  (label "Meta: Muse Spark 1.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta/muse-spark-1.1)
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
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.00000125")
    (completion "0.00000425")
    (web_search "0.0025")
    (input_cache_read "0.00000015")
  ))
  (properties (
    (id meta/muse-spark-1.1)
    (canonical_slug meta/muse-spark-1.1-20260709)
    (hugging_face_id null)
    (name "Meta: Muse Spark 1.1")
    (created 1784215741)
    (description "Muse Spark 1.1 is a multimodal reasoning model from Meta, built for agentic tasks. It accepts text, images, video, audio, and PDF documents and returns text, with a 1M-token context...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        video
        file
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00000425")
      (web_search "0.0025")
      (input_cache_read "0.00000015")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens null)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta/muse-spark-1.1-20260709/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1193)
          (win_rate 48.2)
          (rank 8)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1141)
          (win_rate 39.4)
          (rank 20)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1217)
          (win_rate 51.6)
          (rank 8)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1173)
          (win_rate 44.1)
          (rank 12)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1254)
          (win_rate 51)
          (rank 11)
        )
        (
          (arena models)
          (category 3d)
          (elo 1300)
          (win_rate 52.7)
          (rank 18)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1323)
          (win_rate 61.2)
          (rank 3)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1308)
          (win_rate 54.8)
          (rank 9)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1320)
          (win_rate 55.4)
          (rank 7)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1326)
          (win_rate 55.8)
          (rank 7)
        )
        (
          (arena models)
          (category svg)
          (elo 1266)
          (win_rate 50.5)
          (rank 9)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1329)
          (win_rate 54.9)
          (rank 7)
        )
        (
          (arena models)
          (category website)
          (elo 1295)
          (win_rate 53.9)
          (rank 16)
        )
      ))
      (artificial_analysis (
        (intelligence_index 53.2)
        (coding_index 71.3)
        (agentic_index 39.7)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta/muse-spark-1.1)
    (canonical_slug meta/muse-spark-1.1-20260709)
    (hugging_face_id null)
    (name "Meta: Muse Spark 1.1")
    (created 1784215741)
    (description "Muse Spark 1.1 is a multimodal reasoning model from Meta, built for agentic tasks. It accepts text, images, video, audio, and PDF documents and returns text, with a 1M-token context...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        video
        file
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00000425")
      (web_search "0.0025")
      (input_cache_read "0.00000015")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens null)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta/muse-spark-1.1-20260709/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1193)
          (win_rate 48.2)
          (rank 8)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1141)
          (win_rate 39.4)
          (rank 20)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1217)
          (win_rate 51.6)
          (rank 8)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1173)
          (win_rate 44.1)
          (rank 12)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1254)
          (win_rate 51)
          (rank 11)
        )
        (
          (arena models)
          (category 3d)
          (elo 1300)
          (win_rate 52.7)
          (rank 18)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1323)
          (win_rate 61.2)
          (rank 3)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1308)
          (win_rate 54.8)
          (rank 9)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1320)
          (win_rate 55.4)
          (rank 7)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1326)
          (win_rate 55.8)
          (rank 7)
        )
        (
          (arena models)
          (category svg)
          (elo 1266)
          (win_rate 50.5)
          (rank 9)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1329)
          (win_rate 54.9)
          (rank 7)
        )
        (
          (arena models)
          (category website)
          (elo 1295)
          (win_rate 53.9)
          (rank 16)
        )
      ))
      (artificial_analysis (
        (intelligence_index 53.2)
        (coding_index 71.3)
        (agentic_index 39.7)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta/muse-spark-1.1)
  ))
)
