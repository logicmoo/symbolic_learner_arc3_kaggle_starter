import type { WorkflowStepDefinition } from "./workflowTypes";

export const workflowSteps: WorkflowStepDefinition[] = [
  { id: "grab_image_source", order: 1, title: "Acquire Input", shortTitle: "Input", description: "Load an ARC3 state, image, video frame, upload, or disk artifact.", consumes: ["video", "arc3_state", "file_reference"], produces: ["image"] },
  { id: "turtlize_objects", order: 2, title: "Extract and Turtlize Objects", shortTitle: "Objects", description: "Detect objects and generate stable identities plus symbolic Turtle representations.", consumes: ["image", "object_annotation"], produces: ["turtle_program", "object_annotation"] },
  { id: "run_prolog_checks", order: 3, title: "Construct and Verify Facts", shortTitle: "Prolog", description: "Generate Prolog facts and verify symbolic object properties and identities.", consumes: ["prolog_facts", "turtle_program"], produces: ["execution_log", "object_annotation"] },
  { id: "rule_induction", order: 4, title: "Induce Rules", shortTitle: "Rules", description: "Infer transformations and reusable symbolic rules from examples.", consumes: ["execution_log", "artifact_bundle"], produces: ["rule_set", "prolog_program"] },
  { id: "apply_rules_to_image", order: 5, title: "Apply Rules", shortTitle: "Apply", description: "Apply an induced rule to an image, scene, or individual object.", consumes: ["image", "rule_set"], produces: ["image", "object_annotation"] },
  { id: "compare_artifacts", order: 6, title: "Compare Results", shortTitle: "Compare", description: "Compare images, Turtle programs, Prolog facts, predictions, and expected outputs.", consumes: ["image", "turtle_program", "prolog_program", "rule_set"], produces: ["score", "change_description"] },
  { id: "images_displayer", order: 7, title: "Display Analysis", shortTitle: "Display", description: "Render source, expected, predicted, and difference views.", consumes: ["image", "artifact_bundle"], produces: ["artifact_bundle"] },
  { id: "turtlized_objects_to_images", order: 8, title: "Render Turtle Programs", shortTitle: "Render", description: "Render Turtle programs back into images for visual verification.", consumes: ["turtle_program"], produces: ["turtle_drawing", "image"] },
  { id: "make_dataset", order: 9, title: "Build Dataset", shortTitle: "Dataset", description: "Collect object packages, comparisons, examples, and provenance.", consumes: ["object_annotation", "change_description"], produces: ["artifact_bundle"] },
  { id: "save_to_disk", order: 10, title: "Persist Artifacts", shortTitle: "Save", description: "Write JSON, Turtle, Prolog, image, and Markdown artifacts to disk.", consumes: ["artifact_bundle"], produces: ["file_reference"] },
];
