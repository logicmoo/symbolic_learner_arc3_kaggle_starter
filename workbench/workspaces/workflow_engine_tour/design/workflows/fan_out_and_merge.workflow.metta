(
  (id fan_out_and_merge)
  (label "Fan out and merge")
  (generation (
    (operation workflow.populate_from_english)
    (englishDescriptionPath docs/WORKFLOW_DESCRIPTION.md)
    (operationCategories ([]
      workflow-language
    ))
    (preflightRequired true)
  ))
  (inputs (
    (items Array)
  ))
  (outputs (
    (values $values)
  ))
  (steps ([]
    (
      (id map_items)
      (kind operation)
      (implementation core.echo)
      (inputs (
        (value $item)
      ))
      (foreach (
        (items $items)
        (itemPort value)
        (maxItems 20)
      ))
      (outputs (
        (value values)
      ))
    )
    (
      (id collect_values)
      (kind operation)
      (implementation core.collect)
      (dependsOn ([]
        map_items
      ))
      (inputs (
        (items $values)
      ))
      (outputs (
        (value values)
      ))
    )
  ))
  (kind workflow)
  (workspaceId workflow_engine_tour)
  (captureGroupPlan ([]
    (
      (id repeated-output:values)
      (inference repeated_output_binding)
      (markerName values)
      (iterationCount 2)
      (iterations ([]
        (
          (iteration 1)
          (startStepId map_items)
          (endStepId map_items)
          (memberStepIds ([]
            map_items
          ))
        )
        (
          (iteration 2)
          (startStepId collect_values)
          (endStepId collect_values)
          (memberStepIds ([]
            collect_values
          ))
        )
      ))
    )
  ))
)
