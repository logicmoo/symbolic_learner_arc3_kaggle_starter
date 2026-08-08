(
  (kind model)
  (id gpt-5.6)
  (label GPT-5.6)
  (description "Base GPT-5.6 model configuration inheriting from the shared OpenAI backend.")
  (inherits openai)
  (model gpt-5.6)
  (enabled true)
  (example_execute (
    (action model.invoke)
    (arguments (
      (prompt (
        (datatype Text)
        (label Prompt)
        (default "Reply with the title-case form of: the quick brown fox")
      ))
    ))
  ))
  (capabilities ([]
    text
    vision
    reasoning
    json
  ))
  (defaults (
    (reasoningEffort medium)
    (maxOutputTokens 16000)
    (temperature 0)
    (topP 1)
    (timeoutSeconds 300)
    (currentImageDetail high)
    (parentImageDetail high)
    (analysisLevel 1)
  ))
  (environment (
    (model WORKBENCH_OPENAI_MODEL)
    (legacyModel ARC3_OPENAI_MODEL)
  ))
)
