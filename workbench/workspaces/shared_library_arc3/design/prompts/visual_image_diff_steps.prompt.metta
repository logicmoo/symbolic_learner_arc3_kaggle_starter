(
  (kind prompt)
  (id visual_image_diff.output_contract)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName output-contract)
  (classificationId visual_image_diff.010.output_contract)
  (produces ([] response_contract))
  (label "Strict JSON Output Contract")
  (description "Require the exact seven-part ARC3 visual-analysis response envelope.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "Analyze the current ARC3 state and return exactly one valid JSON object. Do not return Markdown, commentary, or keys other than: new_identities, objects_pl, differences_pl, similarities_pl, turtle_from_image_pl, turtle_from_diff_pl, and rules_pl. new_identities must be a JSON array. Every *_pl value must be a JSON string containing plain SWI-Prolog source. Escape all newlines, quotation marks, backslashes, and control characters as required by strict JSON. The decoded string must contain Prolog source without Markdown fences."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.coordinate_contract)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName coordinates)
  (classificationId visual_image_diff.020.coordinates)
  (produces ([] logical_geometry))
  (label "Logical Grid Coordinate Contract")
  (description "Keep all geometry in the logical ARC grid rather than display pixels.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "Reason exclusively in the logical ARC grid, normally 64x64 cells, rather than enlarged PNG display pixels. Use zero-based coordinates. x increases to the right and y increases downward. Never report 512x512 display-pixel geometry when the underlying board is 64x64. Describe exact cells, compact cell runs, logical bounding boxes, and connected components."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.identity_contract)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName identities)
  (classificationId visual_image_diff.030.identities)
  (produces ([] new_identities))
  (label "Canonical Identity Contract")
  (description "Reuse canonical object identities and isolate genuinely new identities.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "object_registry.pl is the canonical identity source. Reuse every established friendly ID exactly. new_identities must contain only genuinely new semantic objects, each represented as a JSON object with exactly the fields id, type, and label. Never invent opaque IDs such as obj_1, object_7, or region_a. Do not repeat established object_identity/3 declarations in objects_pl. Newly proposed identities belong only in new_identities during this response."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.object_extraction)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName objects)
  (classificationId visual_image_diff.040.objects)
  (produces ([] objects_pl))
  (label "Current-State Object Extraction")
  (description "Extract meaningful objects and supported spatial facts without redundancy.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "objects_pl must describe the current state comprehensively but nonredundantly. Detect meaningful connected color regions and useful block-level structures, including blocks, rectangles, bars, line segments, glyphs, holes, enclosures, borders, HUD elements, status indicators, compound objects, and meaningful sub-objects. Do not treat every individual cell as a separate object unless the cell has an independent semantic role."
    "For each object, emit object/3 and all applicable facts selected from: color/2, colors/2, bbox/5, size/3, area/2, occupied_cells/2, cell_runs/2, shape/2, orientation/2, component_of/2, contains/2, inside/2, adjacent/2, touches/2, overlaps/2, aligned_with/3, symmetry/2, role/2, and confidence/2. Emit only predicates supported by visible evidence. Prefer cell_runs/2 over occupied_cells/2 for large regular regions. Preserve exact topology, connectivity, cavities, holes, borders, and enclosure relationships."
    "objects_pl contains only current-state facts and turtle_program/2 facts associated with canonical objects. It must not contain object_identity/3 declarations, parent-transition facts, cross-state correspondences, or rule hypotheses."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.turtle_reconstruction)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName turtle-image)
  (classificationId visual_image_diff.050.turtle_image)
  (produces ([] turtle_from_image_pl))
  (label "Turtle Full-Frame Reconstruction")
  (description "Reconstruct the current logical grid with motion-based Turtle programs.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "turtle_from_image_pl must faithfully reconstruct the complete current logical grid as motion-based Turtle programs. The canonical drawing vocabulary is penup, pendown, set_pos/2, setcolor/1, pen_width/1, fwd/1, rot/1, and set_cell. pen_width/1 accepts only widths 1 through 4 logical cells. Use set_pos/2 only to establish an initial position or begin a genuinely disconnected stroke. Once positioned, trace geometry with fwd/1 and rot/1. Prefer the largest exact pen width up to 4."
    "Do not generate rect/4, rectangle/4, fill/1, block/4, draw_cells/1, direct four-coordinate box commands, or long lists of independent cell placements. Draw borders by moving and rotating around their perimeter and solid regions as motion-based scan lines. Preserve holes rather than painting oversized blocks."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.turtle_patch)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName turtle-diff)
  (classificationId visual_image_diff.060.turtle_diff)
  (produces ([] turtle_from_diff_pl))
  (label "Turtle Parent-to-Current Patch")
  (description "Generate a minimal executable patch covering every changed logical cell.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "turtle_from_diff_pl must provide an executable and complete parent-to-current motion-based patch covering exactly the changed cells whenever possible. It must include cells that were cleared, overwritten, recolored, added, or restored. Minimize the patch by changed logical cells, use pen_width/1 for exact parallel changes, and never omit a required change merely to make the program shorter. The diff program must obey the same prohibition on rect/4 and direct block commands."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.transitions)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName transitions)
  (classificationId visual_image_diff.070.transitions)
  (produces ([] differences_pl))
  (label "Direct Transition Evidence")
  (description "Describe only evidenced parent-to-current changes.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "differences_pl must contain direct parent-to-current observations only. Represent applicable changes such as unchanged, moved, appeared, disappeared, recolored, resized, reshaped, split, merged, opened, closed, consumed, created, destroyed, overwritten, or HUD/status changes. Every claimed transition must include concrete coordinate, color, geometry, or cell-set evidence. Do not infer a game rule in differences_pl."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.correspondences)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName correspondences)
  (classificationId visual_image_diff.080.correspondences)
  (produces ([] similarities_pl))
  (label "Persistent Object Correspondences")
  (description "Match persistent objects across parent and current states only when supported.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "similarities_pl must contain parent-to-current object correspondences only. Record persistent-object matches, similarity scores, matched properties, changed properties, and supporting evidence. Do not force a correspondence when appearance or disappearance is better supported. Reuse canonical IDs from object_registry.pl."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.rule_analysis)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName rules)
  (classificationId visual_image_diff.090.rules)
  (produces ([] rules_pl))
  (label "Evidence-Grounded Rule Analysis")
  (description "Separate observations, hypotheses, support, contradictions, and confidence.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "rules_pl must separate observed_rule/2, hypothetical_rule/3, evidence/3, supported_by/2, contradicted_by/2, and confidence/2. observed_rule/2 is reserved for directly established transition regularities. hypothetical_rule/3 must clearly identify assumptions or unresolved alternatives. Evidence must cite concrete state or transition facts rather than restating the hypothesis. Do not promote a hypothesis to an observed rule from a single ambiguous coincidence."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.file_separation)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName separation)
  (classificationId visual_image_diff.100.file_separation)
  (produces ([] resource_separation))
  (label "Analysis Resource Separation")
  (description "Keep identities, state, transitions, correspondences, Turtle code, and rules separate.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "Put proposed identities only in new_identities; current-state facts only in objects_pl; direct transition facts only in differences_pl; cross-state correspondences only in similarities_pl; full-frame drawing code only in turtle_from_image_pl; changed-cell patch code only in turtle_from_diff_pl; and rule hypotheses, rule evidence, support links, contradictions, and rule confidence only in rules_pl."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.root_state)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName root-state)
  (classificationId visual_image_diff.110.root_state)
  (produces ([] root_state_behavior))
  (label "Root-State Behavior")
  (description "Define empty diff behavior when no parent image exists.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "When the current state has no parent, differences_pl, similarities_pl, and turtle_from_diff_pl must be empty strings. rules_pl may still contain current-state hypotheses only when they are explicitly marked hypothetical and do not claim parent-transition evidence."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.quality_control)
  (applicability ([] visual_image_diff.analysis_step))
  (buttonName quality)
  (classificationId visual_image_diff.120.quality_control)
  (produces ([] validation_report))
  (label "Final Quality Control")
  (description "Validate strict JSON, coordinates, identities, and Prolog syntax before returning.")
  (targets ([] vision reasoning-chat))
  (text ([]
    "Before returning, verify that the result parses as strict JSON, contains exactly the seven required keys, uses no Markdown fences, uses no opaque object IDs, uses only logical grid coordinates, and contains syntactically plausible SWI-Prolog source in every nonempty *_pl string."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.source)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-source)
  (classificationId visual_image_diff.000.pipeline.010.source)
  (produces ([] source_images source_manifest))
  (label "Pipeline — Grab Image Source")
  (description "Acquire the ordered source images and their manifest from ARC3 state.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"source\",\"task\":\"grab_image_source\",\"implementation\":\"arc3_state\",\"parameters\":{},\"outputs\":{\"images\":\"source_images\",\"manifest\":\"source_manifest\"}}. The submitted image sequence is the source collection for every later stage."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.normalize)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-normalize)
  (classificationId visual_image_diff.000.pipeline.020.normalize)
  (produces ([] normalized_images normalized_manifest))
  (label "Pipeline — Normalize Image Collection")
  (description "Normalize the source collection as PNG images with a matching manifest.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"normalize\",\"task\":\"normalize_image_collection\",\"implementation\":\"pillow_png\",\"inputs\":{\"images\":\"source_images\"},\"outputs\":{\"images\":\"normalized_images\",\"manifest\":\"normalized_manifest\"}}."
    "Normalize geometry into the logical ARC grid, normally 64x64 cells, with zero-based x-right/y-down coordinates. The manifest must describe logical cells, runs, bounding boxes, and connected components rather than enlarged display pixels."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.objects)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-objects)
  (classificationId visual_image_diff.000.pipeline.030.objects)
  (produces ([] scene_objects object_manifest turtle_programs objects_pl turtle_from_image_pl))
  (label "Pipeline — Extract Individual Objects")
  (description "Use the requested vision model profile to extract objects and Turtle programs.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"objects\",\"task\":\"extract_individual_objects\",\"implementation\":\"vision_llm\",\"profile\":\"openai-gpt-5.6-light\",\"inputs\":{\"images\":\"normalized_images\"},\"outputs\":{\"objects\":\"scene_objects\",\"object_manifest\":\"object_manifest\",\"turtle\":\"turtle_programs\"}}."
    "Merged alias contract: {\"id\":\"extract_scene_objects\",\"kind\":\"llm_artifacts\",\"requires_vision\":true,\"include_parent_image\":true,\"include_current_image\":true,\"output_keys\":[\"objects_pl\",\"turtle_from_image_pl\"],\"input_files\":[\"object_registry.pl\"],\"combine_safe\":true}. This is the same object-extraction stage, not another stage."
    "Reuse established friendly identities from object_registry.pl and propose only genuinely new friendly identities. Extract meaningful connected objects, topology, holes, enclosures, exact logical geometry, and supported spatial relations without treating every cell as a separate object. Generate faithful motion-based Turtle programs using penup, pendown, set_pos/2, setcolor/1, pen_width/1, fwd/1, rot/1, and set_cell; preserve holes and do not use rect/4 or direct block commands."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.sync_representations)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-sync)
  (classificationId visual_image_diff.000.pipeline.040.sync_representations)
  (produces ([] object_manifest))
  (label "Pipeline — Synchronize Object Representations")
  (description "Synchronize object, image, and manifest representations before rendering.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"sync_representations\",\"task\":\"synchronize_object_representations\",\"implementation\":\"python_manifest\",\"inputs\":{\"objects\":\"scene_objects\",\"images\":\"normalized_images\"},\"outputs\":{\"object_manifest\":\"object_manifest\"}}."
    "Keep proposed identities, current-state object facts, transition facts, cross-state correspondences, full-frame Turtle code, changed-cell Turtle patches, and rule evidence in their separate named resources while synchronizing their shared canonical object identifiers."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.render_turtle)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-render)
  (classificationId visual_image_diff.000.pipeline.050.render_turtle)
  (produces ([] turtle_images turtle_render_manifest))
  (label "Pipeline — Render Turtle Objects")
  (description "Render Turtle programs back into images for comparison and inspection.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"render_turtle\",\"task\":\"turtlized_objects_to_images\",\"implementation\":\"python_turtle_renderer\",\"inputs\":{\"turtle\":\"turtle_programs\",\"objects\":\"object_manifest\"},\"outputs\":{\"images\":\"turtle_images\",\"render_manifest\":\"turtle_render_manifest\"}}."
    "Render the complete logical grid from the motion-based Turtle vocabulary and record exact reconstruction fit, residual, and any unsupported drawing command in turtle_render_manifest."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.display)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-display)
  (classificationId visual_image_diff.000.pipeline.060.display)
  (produces ([] display_session))
  (label "Pipeline — Display Rendered Images")
  (description "Open the rendered Turtle image collection without making display failure fatal.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"display\",\"task\":\"images_displayer\",\"implementation\":\"python_image_viewer\",\"inputs\":{\"images\":\"turtle_images\"},\"outputs\":{\"display_session\":\"display_session\"},\"continue_on_error\":true}."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.compare)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-compare)
  (classificationId visual_image_diff.000.pipeline.070.compare)
  (produces ([] transition_evidence differences_pl similarities_pl turtle_from_diff_pl))
  (label "Pipeline — Compare Scene Objects")
  (description "Compare source, normalized, and object manifests with the requested symbolic profile.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"compare\",\"task\":\"compare_scene_objects\",\"implementation\":\"symbolic_llm\",\"profile\":\"groq-qwen-3.6-27b-deep\",\"inputs\":{\"before\":\"source_manifest\",\"after\":\"normalized_manifest\",\"objects\":\"object_manifest\"},\"outputs\":{\"transition\":\"transition_evidence\"}}."
    "Merged alias contract: {\"id\":\"explain_object_changes\",\"kind\":\"llm_artifacts\",\"requires_vision\":false,\"include_parent_image\":false,\"include_current_image\":false,\"output_keys\":[\"differences_pl\",\"similarities_pl\",\"turtle_from_diff_pl\"],\"input_files\":[\"object_registry.pl\",\"objects.pl\",\"turtle_from_image.pl\",\"differences.pl\",\"similarities.pl\",\"turtle_from_diff.pl\"],\"combine_safe\":true}. This is the symbolic comparison stage, not another stage."
    "Use the symbolic object and Turtle files to explain exact parent-to-current changes, supported persistent-object correspondences, and a minimal executable changed-cell Turtle patch. Keep direct observations separate from rule hypotheses. When no parent exists, emit empty differences, similarities, and Turtle-diff resources."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.rules)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-rules)
  (classificationId visual_image_diff.000.pipeline.080.rules)
  (produces ([] rule_set rules_pl))
  (label "Pipeline — Induce Transition Rules")
  (description "Induce rules from transition evidence and the synchronized object manifest.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"rules\",\"task\":\"induce_transition_rules\",\"implementation\":\"rule_llm\",\"profile\":\"openrouter-north-mini-code-rules\",\"inputs\":{\"transition\":\"transition_evidence\",\"objects\":\"object_manifest\"},\"outputs\":{\"rules\":\"rule_set\"}}."
    "Merged alias contract: {\"id\":\"induce_rules_from_prolog\",\"kind\":\"llm_artifacts\",\"requires_vision\":false,\"include_parent_image\":false,\"include_current_image\":false,\"output_keys\":[\"rules_pl\"],\"input_files\":[\"object_registry.pl\",\"objects.pl\",\"differences.pl\",\"similarities.pl\",\"turtle_from_image.pl\",\"turtle_from_diff.pl\",\"rules.pl\"],\"combine_safe\":false}. This is the same conservative rule-induction stage. Separate observed rules, hypotheses, supporting evidence, contradictions, and confidence."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.cherry_pick)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-cherry-pick)
  (classificationId visual_image_diff.000.pipeline.090.cherry_pick)
  (produces ([] artifact_bundle prolog_validation))
  (label "Pipeline — Prolog Cherry-Pick Evidence")
  (description "Use Prolog analysis to retain supported evidence while preserving the bundle on failure.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"cherry_pick\",\"task\":\"prolog_cherry_pick_evidence\",\"implementation\":\"prolog_full_analysis\",\"inputs\":{\"bundle\":\"artifact_bundle\"},\"outputs\":{\"bundle\":\"artifact_bundle\",\"validation\":\"prolog_validation\"},\"continue_on_error\":true}."
    "Merged runner alias: {\"id\":\"prolog_render_symbolic_evidence\",\"kind\":\"runner_method\",\"runner_method\":\"prolog_command_4\",\"requires_vision\":false,\"combine_safe\":false}. Treat prolog_command_4 as the concrete runner route for the same Prolog evidence pass, not a separate prompt stage."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.validate)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-validate)
  (classificationId visual_image_diff.000.pipeline.100.validate)
  (produces ([] validation_report audit_report))
  (label "Pipeline — Validate Artifact Bundle")
  (description "Validate the assembled bundle and produce both validation and audit reports.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"validate\",\"task\":\"validate_artifact_bundle\",\"implementation\":\"python_validator\",\"inputs\":{\"bundle\":\"artifact_bundle\"},\"outputs\":{\"validation\":\"validation_report\",\"audit\":\"audit_report\"}}."
    "Merged audit contract: {\"id\":\"audit_artifact_bundle\",\"kind\":\"llm_text\",\"requires_vision\":false,\"include_parent_image\":false,\"include_current_image\":false,\"output_file\":\"artifact_audit.md\",\"input_files\":[\"object_registry.pl\",\"objects.pl\",\"differences.pl\",\"similarities.pl\",\"turtle_from_image.pl\",\"turtle_from_diff.pl\",\"rules.pl\"],\"combine_safe\":false}. This is the audit facet of validation, not another stage. Verify strict JSON/resource syntax, logical coordinates, friendly identities, Prolog plausibility, and completeness before producing audit_md."
  ))
)

(
  (kind prompt)
  (id visual_image_diff.pipeline.report)
  (applicability ([] visual_image_diff.pipeline_step))
  (buttonName pipeline-report)
  (classificationId visual_image_diff.000.pipeline.110.report)
  (produces ([] workflow_report))
  (label "Pipeline — Publish Workflow Report")
  (description "Publish the final artifact and validation bundle as a Markdown report.")
  (targets ([] vision workflow-generation))
  (text ([]
    "Preserve this workflow-stage contract exactly: {\"id\":\"report\",\"task\":\"publish_workflow_report\",\"implementation\":\"markdown_report\",\"inputs\":{\"bundle\":\"artifact_bundle\",\"validation\":\"validation_report\"},\"outputs\":{\"report\":\"workflow_report\"}}."
  ))
)

(
  (kind prompt_profile)
  (id visual_image_diff.analysis_group)
  (label "ARC3 Visual Image Diff — Pipeline and Analysis Group")
  (description "The ordered image-processing pipeline and ARC3 visual analysis contract represented as one reusable prompt group.")
  (separator "\n\n")
  (prompts ([]
    visual_image_diff.pipeline.source
    visual_image_diff.pipeline.normalize
    visual_image_diff.pipeline.objects
    visual_image_diff.pipeline.sync_representations
    visual_image_diff.pipeline.render_turtle
    visual_image_diff.pipeline.display
    visual_image_diff.pipeline.compare
    visual_image_diff.pipeline.rules
    visual_image_diff.pipeline.cherry_pick
    visual_image_diff.pipeline.validate
    visual_image_diff.pipeline.report
  ))
)
