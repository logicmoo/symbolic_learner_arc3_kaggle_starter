(
  (kind backend)
  (id https.llm.c.singularitynet.io.v1)
  (aliases ([]
    snet
    singularitynet
    singularitynet-llm
    https://llm.c.singularitynet.io/v1
  ))
  (label "SingularityNET LLM")
  (provider singularitynet)
  (official true)
  (description "SingularityNET OpenAI-compatible LLM transport. Model resources inherit this backend and provide their provider model identifiers.")
  (enabled true)
  (specializations (
    (https.llm.c.singularitynet.io.v1-asi1-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-asi1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-baai_bge-base-en-v1.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-google_gemma-3-27b-it (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-google_gemma-4-26b-a4b-it (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-google_gemma-4-31b-it (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-meta-llama_llama-3.3-70b-instruct (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-minimax_minimax-m2.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-minimax_minimax-m2.7 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-minimax_minimax-m3-f (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-minimax_minimax-m3 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-mistralai_mistral-nemo (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-nousresearch_hermes-4-70b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-openai_gpt-oss-120b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-openai_gpt-oss-20b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-qwen_qwen3-32b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-qwen_qwen3.8-27b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-qwen_qwen3.5-35b-a3b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-whereisai_uae-large-v1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (https.llm.c.singularitynet.io.v1-z-ai_glm-4.7-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
    (snet-asi1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        specializations
        preferredSpecialization
      ))
    ))
  ))
  (capabilities ([]
    llm.complete
    llm.reasoning
    llm.tools
  ))
  (configuration (
    (adapter openai_chat_completions)
    (baseUrl https://llm.c.singularitynet.io/v1)
    (apiKeyEnvironmentVariable SNET_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_SNET_BASE_URL)
    (modelEnvironmentVariable WORKBENCH_SNET_MODEL)
    (defaultAnalysisLevel 3)
    (timeoutSeconds 900)
  ))
)
