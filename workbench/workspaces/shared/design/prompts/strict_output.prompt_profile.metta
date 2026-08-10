(
  (kind prompt_profile)
  (id strict_output)
  (label "Strict Output Prompt Profile")
  (description "Reusable benchmark composition that emphasizes parseable, wrapper-free output without changing model invocation settings.")
  (enabled true)
  (categories ([]
    prompts/composition
    benchmarks/output-control
  ))
  (prompts ([]
    output_quality_control
  ))
  (separator "\n\n")
)
