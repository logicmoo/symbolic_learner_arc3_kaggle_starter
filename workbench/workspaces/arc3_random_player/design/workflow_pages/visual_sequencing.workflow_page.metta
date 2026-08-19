(
  (kind workflow_page)
  (subkind workflow_page_defiled_by_json)
  (id arc3.visual_sequencing)
  (label "Visual Sequencing")
  (description "Compose and run the ARC3 image-sequence comparison Workflow from filesystem images, commands, Prompt resources, Operations, and accumulated outputs.")
  (glyph ◩)
  (menuPlacement middle)
  (order 30)
  (routeView visualImageDiff)
  (renderer visual_image_diff)
  (layout (
    (kind three_column_accordion)
    (columns ([]
      (
        (id left)
        (label DATA)
        (role data)
        (members ([]
          (
            (id resource_outputs)
            (label "Resource Outputs")
            (component VisualResourceOutputs)
            (initialDisplayMode scroll)
            (outputs (
              (workflowData visual_workflow_data)
              (modelResponse visual_model_response)
            ))
          )
          (
            (id image_command_sequence)
            (label "Image + Command Sequence")
            (component ImageCommandSequence)
            (initialDisplayMode scroll)
            (inputs (
              (manifest visual_image_diff_manifest)
            ))
            (outputs (
              (images visual_sequence_images)
              (commands visual_sequence_commands)
            ))
          )
          (
            (id sequence_context)
            (label "Sequence Context")
            (component VisualSequenceContext)
            (initialDisplayMode scroll)
            (inputs (
              (commands visual_sequence_commands)
            ))
            (outputs (
              (context visual_sequence_context)
            ))
          )
        ))
      )
      (
        (id center)
        (label AUTHORING)
        (role authoring)
        (members ([]
          (
            (id visual_pipeline_subaccordion)
            (label "Generate Visual Diff")
            (component VisualPipelineSubaccordion)
            (initialDisplayMode scroll)
            (inputs (
              (images visual_sequence_images)
              (context visual_sequence_context)
              (prompts effective_prompt_catalog)
              (models effective_model_catalog)
              (composition visual_pipeline_composition)
            ))
            (outputs (
              (composition visual_pipeline_composition)
              (workflowData visual_workflow_data)
            ))
          )
          (
            (id operation_playground)
            (label "Selected Workflow Item + Operation Playground")
            (component SelectedOperationPlayground)
            (initialDisplayMode strip)
            (inputs (
              (selection selected_visual_transaction)
              (workflowData visual_workflow_data)
            ))
            (outputs (
              (workflowData visual_workflow_data)
            ))
          )
        ))
      )
      (
        (id right)
        (label "SOURCE DETAILS")
        (role details)
        (members ([]
          (
            (id visual_sequencing_page_source)
            (label "CURRENT PAGE SPECIFICATION")
            (component ResourceSourceEditor)
            (initialDisplayMode strip)
            (resource (
              (kind workflow_page)
              (id arc3.visual_sequencing)
            ))
            (options (
              (format json)
              (editable true)
              (validateBeforeApply true)
              (applyOnSave true)
              (preserveLastValidDefinition true)
            ))
            (outputs (
              (source visual_sequencing_page_source)
              (validation visual_sequencing_page_validation)
            ))
          )
          (
            (id composed_group_prompt)
            (label "Composed Group Prompt")
            (component ComposedGroupPrompt)
            (initialDisplayMode scroll)
            (inputs (
              (composition visual_pipeline_composition)
            ))
            (outputs (
              (prompt visual_composed_prompt)
            ))
          )
          (
            (id prompt_source)
            (label "Pipeline — Grab Image Source")
            (component VisualPromptInspector)
            (initialDisplayMode scroll)
            (options (
              (promptId visual_image_diff.pipeline.source)
            ))
          )
          (
            (id prompt_normalize)
            (label "Pipeline — Normalize Image Collection")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.normalize)
            ))
          )
          (
            (id prompt_objects)
            (label "Pipeline — Extract Individual Objects")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.objects)
            ))
          )
          (
            (id prompt_sync)
            (label "Pipeline — Synchronize Object Representations")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.sync_representations)
            ))
          )
          (
            (id prompt_render)
            (label "Pipeline — Render Turtle Objects")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.render_turtle)
            ))
          )
          (
            (id prompt_display)
            (label "Pipeline — Display Rendered Images")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.display)
            ))
          )
          (
            (id prompt_compare)
            (label "Pipeline — Compare Scene Objects")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.compare)
            ))
          )
          (
            (id prompt_rules)
            (label "Pipeline — Induce Transition Rules")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.rules)
            ))
          )
          (
            (id prompt_cherry_pick)
            (label "Pipeline — Prolog Cherry-Pick Evidence")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.cherry_pick)
            ))
          )
          (
            (id prompt_validate)
            (label "Pipeline — Validate Artifact Bundle")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.validate)
            ))
          )
          (
            (id prompt_report)
            (label "Pipeline — Publish Workflow Report")
            (component VisualPromptInspector)
            (initialDisplayMode strip)
            (options (
              (promptId visual_image_diff.pipeline.report)
            ))
          )
        ))
      )
    ))
  ))
)
