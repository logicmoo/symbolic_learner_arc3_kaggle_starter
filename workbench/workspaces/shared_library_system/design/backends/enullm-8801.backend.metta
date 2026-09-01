(
  (kind backend)
  (id enullm-8801)
  (label "EMULLM API at http://127.0.0.1:8801/v1")
  (provider openrouter)
  (official true)
  (description "AIs on WebSockets pretending to be Backend LLM Servers")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.vision
  ))
  (configuration (
    (adapter openai)
    (baseUrl http://127.0.0.1:8801/v1)
    (apiKeyEnvironmentVariable null)
    (baseUrlEnvironmentVariable null)
    (legacyBaseUrlEnvironmentVariable null)
    (defaultModel yourelf.same)
    (modelEnvironmentVariable null)
    (legacyModelEnvironmentVariable null)
    (defaultAnalysisLevel 4)
    (timeoutSeconds 900)
  ))
  (aliases ([]))
  (categories ([]
    backends
    models
    systems/systems-llm
    todo-needs-categorization
    vision
  ))
  (dependedOnBy (
    (enullm-8801-asi1 ())
    (enullm-8801-asi1-mini ())
    (enullm-8801-baai_bge-base-en-v1.5 ())
    (enullm-8801-copilot_auto ())
    (enullm-8801-copilot_claude-fable-5 ())
    (enullm-8801-copilot_claude-haiku-4.5 ())
    (enullm-8801-copilot_claude-opus-4.5 ())
    (enullm-8801-copilot_claude-opus-4.6 ())
    (enullm-8801-copilot_claude-opus-4.7 ())
    (enullm-8801-copilot_claude-opus-4.8 ())
    (enullm-8801-copilot_claude-opus-4.8-fast ())
    (enullm-8801-copilot_claude-opus-5 ())
    (enullm-8801-copilot_claude-sonnet-4.5 ())
    (enullm-8801-copilot_claude-sonnet-4.6 ())
    (enullm-8801-copilot_claude-sonnet-5 ())
    (enullm-8801-copilot_gemini-3.1-pro-preview ())
    (enullm-8801-copilot_gemini-3.5-flash ())
    (enullm-8801-copilot_gemini-3.6-flash ())
    (enullm-8801-copilot_gemini-3.7-flash ())
    (enullm-8801-copilot_gpt-5-mini ())
    (enullm-8801-copilot_gpt-5.3-codex ())
    (enullm-8801-copilot_gpt-5.4 ())
    (enullm-8801-copilot_gpt-5.4-mini ())
    (enullm-8801-copilot_gpt-5.5 ())
    (enullm-8801-copilot_gpt-5.6-luna ())
    (enullm-8801-copilot_gpt-5.6-sol ())
    (enullm-8801-copilot_gpt-5.6-terra ())
    (enullm-8801-copilot_grok-4.5 ())
    (enullm-8801-copilot_grok-4.6 ())
    (enullm-8801-copilot_kimi-k2.7-code ())
    (enullm-8801-copilot_kimi-k3 ())
    (enullm-8801-copilot_mai-code-1-flash-picker ())
    (enullm-8801-copilot_mai-code-1.1-flash ())
    (enullm-8801-deepseek_deepseek-v4-flash-0731 ())
    (enullm-8801-emullm_default ())
    (enullm-8801-google_gemma-4-26b-a4b-it ())
    (enullm-8801-google_gemma-4-31b-it ())
    (enullm-8801-gpt-4o-audio-preview ())
    (enullm-8801-minimax_minimax-m2.7 ())
    (enullm-8801-minimax_minimax-m3 ())
    (enullm-8801-minimax_minimax-m3-f ())
    (enullm-8801-myself_same ())
    (enullm-8801-openai_gpt-oss-120b ())
    (enullm-8801-openai_gpt-oss-20b ())
    (enullm-8801-qwen_qwen3.8-27b ())
    (enullm-8801-whereisai_uae-large-v1 ())
    (enullm-8801-worker-copilot-1_claude-haiku-4.5 ())
    (enullm-8801-worker-copilot-1_gpt-5.4-mini ())
    (enullm-8801-worker-copilot-1_percent10 ())
    (enullm-8801-worker-copilot-1_percent100 ())
    (enullm-8801-worker-copilot-1_percent125 ())
    (enullm-8801-worker-copilot-1_percent25 ())
    (enullm-8801-worker-copilot-1_percent75 ())
    (enullm-8801-worker-copilot-1_same ())
    (enullm-8801-worker-copilot-10_auto ())
    (enullm-8801-worker-copilot-10_percent10 ())
    (enullm-8801-worker-copilot-10_percent100 ())
    (enullm-8801-worker-copilot-10_percent125 ())
    (enullm-8801-worker-copilot-10_percent25 ())
    (enullm-8801-worker-copilot-10_percent75 ())
    (enullm-8801-worker-copilot-10_same ())
    (enullm-8801-worker-copilot-2_gemini-3.1-pro-preview ())
    (enullm-8801-worker-copilot-2_grok-4.5 ())
    (enullm-8801-worker-copilot-2_percent10 ())
    (enullm-8801-worker-copilot-2_percent100 ())
    (enullm-8801-worker-copilot-2_percent125 ())
    (enullm-8801-worker-copilot-2_percent25 ())
    (enullm-8801-worker-copilot-2_percent75 ())
    (enullm-8801-worker-copilot-2_same ())
    (enullm-8801-worker-copilot-3_claude-opus-4.8-fast ())
    (enullm-8801-worker-copilot-3_percent10 ())
    (enullm-8801-worker-copilot-3_percent100 ())
    (enullm-8801-worker-copilot-3_percent125 ())
    (enullm-8801-worker-copilot-3_percent25 ())
    (enullm-8801-worker-copilot-3_percent75 ())
    (enullm-8801-worker-copilot-3_same ())
    (enullm-8801-worker-copilot-4_gemini-3.7-flash ())
    (enullm-8801-worker-copilot-4_gpt-5.5 ())
    (enullm-8801-worker-copilot-4_percent10 ())
    (enullm-8801-worker-copilot-4_percent100 ())
    (enullm-8801-worker-copilot-4_percent125 ())
    (enullm-8801-worker-copilot-4_percent25 ())
    (enullm-8801-worker-copilot-4_percent75 ())
    (enullm-8801-worker-copilot-4_same ())
    (enullm-8801-worker-copilot-5_gemini-3.7-flash ())
    (enullm-8801-worker-copilot-5_percent10 ())
    (enullm-8801-worker-copilot-5_percent100 ())
    (enullm-8801-worker-copilot-5_percent125 ())
    (enullm-8801-worker-copilot-5_percent25 ())
    (enullm-8801-worker-copilot-5_percent75 ())
    (enullm-8801-worker-copilot-5_same ())
    (enullm-8801-yourself_percent10 ())
    (enullm-8801-yourself_percent100 ())
    (enullm-8801-yourself_percent125 ())
    (enullm-8801-yourself_percent25 ())
    (enullm-8801-yourself_percent75 ())
    (enullm-8801-yourself_same ())
    (enullm-8801-zira_for_sol ())
  ))
  (implementedBy (
    (enullm-8801-asi1 ())
    (enullm-8801-asi1-mini ())
    (enullm-8801-baai_bge-base-en-v1.5 ())
    (enullm-8801-copilot_auto ())
    (enullm-8801-copilot_claude-fable-5 ())
    (enullm-8801-copilot_claude-haiku-4.5 ())
    (enullm-8801-copilot_claude-opus-4.5 ())
    (enullm-8801-copilot_claude-opus-4.6 ())
    (enullm-8801-copilot_claude-opus-4.7 ())
    (enullm-8801-copilot_claude-opus-4.8 ())
    (enullm-8801-copilot_claude-opus-4.8-fast ())
    (enullm-8801-copilot_claude-opus-5 ())
    (enullm-8801-copilot_claude-sonnet-4.5 ())
    (enullm-8801-copilot_claude-sonnet-4.6 ())
    (enullm-8801-copilot_claude-sonnet-5 ())
    (enullm-8801-copilot_gemini-3.1-pro-preview ())
    (enullm-8801-copilot_gemini-3.5-flash ())
    (enullm-8801-copilot_gemini-3.6-flash ())
    (enullm-8801-copilot_gemini-3.7-flash ())
    (enullm-8801-copilot_gpt-5-mini ())
    (enullm-8801-copilot_gpt-5.3-codex ())
    (enullm-8801-copilot_gpt-5.4 ())
    (enullm-8801-copilot_gpt-5.4-mini ())
    (enullm-8801-copilot_gpt-5.5 ())
    (enullm-8801-copilot_gpt-5.6-luna ())
    (enullm-8801-copilot_gpt-5.6-sol ())
    (enullm-8801-copilot_gpt-5.6-terra ())
    (enullm-8801-copilot_grok-4.5 ())
    (enullm-8801-copilot_grok-4.6 ())
    (enullm-8801-copilot_kimi-k2.7-code ())
    (enullm-8801-copilot_kimi-k3 ())
    (enullm-8801-copilot_mai-code-1-flash-picker ())
    (enullm-8801-copilot_mai-code-1.1-flash ())
    (enullm-8801-deepseek_deepseek-v4-flash-0731 ())
    (enullm-8801-emullm_default ())
    (enullm-8801-google_gemma-4-26b-a4b-it ())
    (enullm-8801-google_gemma-4-31b-it ())
    (enullm-8801-gpt-4o-audio-preview ())
    (enullm-8801-minimax_minimax-m2.7 ())
    (enullm-8801-minimax_minimax-m3 ())
    (enullm-8801-minimax_minimax-m3-f ())
    (enullm-8801-myself_same ())
    (enullm-8801-openai_gpt-oss-120b ())
    (enullm-8801-openai_gpt-oss-20b ())
    (enullm-8801-qwen_qwen3.8-27b ())
    (enullm-8801-whereisai_uae-large-v1 ())
    (enullm-8801-worker-copilot-1_claude-haiku-4.5 ())
    (enullm-8801-worker-copilot-1_gpt-5.4-mini ())
    (enullm-8801-worker-copilot-1_percent10 ())
    (enullm-8801-worker-copilot-1_percent100 ())
    (enullm-8801-worker-copilot-1_percent125 ())
    (enullm-8801-worker-copilot-1_percent25 ())
    (enullm-8801-worker-copilot-1_percent75 ())
    (enullm-8801-worker-copilot-1_same ())
    (enullm-8801-worker-copilot-10_auto ())
    (enullm-8801-worker-copilot-10_percent10 ())
    (enullm-8801-worker-copilot-10_percent100 ())
    (enullm-8801-worker-copilot-10_percent125 ())
    (enullm-8801-worker-copilot-10_percent25 ())
    (enullm-8801-worker-copilot-10_percent75 ())
    (enullm-8801-worker-copilot-10_same ())
    (enullm-8801-worker-copilot-2_gemini-3.1-pro-preview ())
    (enullm-8801-worker-copilot-2_grok-4.5 ())
    (enullm-8801-worker-copilot-2_percent10 ())
    (enullm-8801-worker-copilot-2_percent100 ())
    (enullm-8801-worker-copilot-2_percent125 ())
    (enullm-8801-worker-copilot-2_percent25 ())
    (enullm-8801-worker-copilot-2_percent75 ())
    (enullm-8801-worker-copilot-2_same ())
    (enullm-8801-worker-copilot-3_claude-opus-4.8-fast ())
    (enullm-8801-worker-copilot-3_percent10 ())
    (enullm-8801-worker-copilot-3_percent100 ())
    (enullm-8801-worker-copilot-3_percent125 ())
    (enullm-8801-worker-copilot-3_percent25 ())
    (enullm-8801-worker-copilot-3_percent75 ())
    (enullm-8801-worker-copilot-3_same ())
    (enullm-8801-worker-copilot-4_gemini-3.7-flash ())
    (enullm-8801-worker-copilot-4_gpt-5.5 ())
    (enullm-8801-worker-copilot-4_percent10 ())
    (enullm-8801-worker-copilot-4_percent100 ())
    (enullm-8801-worker-copilot-4_percent125 ())
    (enullm-8801-worker-copilot-4_percent25 ())
    (enullm-8801-worker-copilot-4_percent75 ())
    (enullm-8801-worker-copilot-4_same ())
    (enullm-8801-worker-copilot-5_gemini-3.7-flash ())
    (enullm-8801-worker-copilot-5_percent10 ())
    (enullm-8801-worker-copilot-5_percent100 ())
    (enullm-8801-worker-copilot-5_percent125 ())
    (enullm-8801-worker-copilot-5_percent25 ())
    (enullm-8801-worker-copilot-5_percent75 ())
    (enullm-8801-worker-copilot-5_same ())
    (enullm-8801-yourself_percent10 ())
    (enullm-8801-yourself_percent100 ())
    (enullm-8801-yourself_percent125 ())
    (enullm-8801-yourself_percent25 ())
    (enullm-8801-yourself_percent75 ())
    (enullm-8801-yourself_same ())
    (enullm-8801-zira_for_sol ())
  ))
  (inheritedBy (
    (enullm-8801-asi1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-asi1-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-baai_bge-base-en-v1.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_auto (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-fable-5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-haiku-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-4.6 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-4.7 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-4.8 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-4.8-fast (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-opus-5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-sonnet-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-sonnet-4.6 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_claude-sonnet-5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gemini-3.1-pro-preview (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gemini-3.5-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gemini-3.6-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gemini-3.7-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.3-codex (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.4 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.4-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.6-luna (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.6-sol (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_gpt-5.6-terra (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_grok-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_grok-4.6 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_kimi-k2.7-code (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_kimi-k3 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_mai-code-1-flash-picker (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-copilot_mai-code-1.1-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-deepseek_deepseek-v4-flash-0731 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-emullm_default (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-google_gemma-4-26b-a4b-it (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-google_gemma-4-31b-it (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-gpt-4o-audio-preview (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-minimax_minimax-m2.7 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-minimax_minimax-m3 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-minimax_minimax-m3-f (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-myself_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-openai_gpt-oss-120b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-openai_gpt-oss-20b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-qwen_qwen3.8-27b (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-whereisai_uae-large-v1 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_claude-haiku-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_gpt-5.4-mini (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-1_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_auto (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-10_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_gemini-3.1-pro-preview (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_grok-4.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-2_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_claude-opus-4.8-fast (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-3_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_gemini-3.7-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_gpt-5.5 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-4_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_gemini-3.7-flash (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-worker-copilot-5_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-yourself_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
    (enullm-8801-zira_for_sol (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
  ))
)
