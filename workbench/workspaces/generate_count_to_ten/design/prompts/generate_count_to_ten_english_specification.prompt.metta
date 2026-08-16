(
  (kind prompt)
  (id generate_count_to_ten.english_workflow_specification)
  (label "Generate Count to Ten / English Workflow Specification")
  (description "The authoritative plain-English resource from which the test workflow is generated.")
  (version 1)
  (targets ([] generic-chat reasoning-chat))
  (text ([]
    "Create a bounded semantic workflow that counts from 1 through 10 inclusive and returns the ordered values."
    "Initialize a workflow-scoped AtomSpace memory cell named current_count to 1 and an ordered collected_values cell to an empty list."
    "For each iteration, read current_count, append that number to collected_values, and retain evidence linking the produced number to its iteration."
    "While current_count is less than 10, increment current_count by one and repeat the capture step. The loop must have an explicit maximum of 10 iterations and must not produce 11."
    "Use shared semantic operations such as value.compare, memory.read, memory.write, control.while, control.loop.continue, and control.return when their contracts fit."
    "Declare atomspace_scope, atomspace_scope_key, atomspace_cell, atomspace_atom, change_mode, and evidenceLink explicitly for every memory mutation."
    "Preflight must identify collected_values as an iteration accumulation and current_count as a retained loop value."
    "Return count_values equal to [1,2,3,4,5,6,7,8,9,10], final_count equal to 10, and loop evidence sufficient to verify every iteration."
    "Generate semantic operation references first. Do not select or invent Python, Prolog, or LLM implementations while constructing the workflow; resolve implementations only after the complete workflow passes preflight."
  ))
)
