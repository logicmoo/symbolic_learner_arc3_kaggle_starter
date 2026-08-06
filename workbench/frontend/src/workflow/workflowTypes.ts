import type { DataType } from "../artifacts/artifactTypes";

export type WorkflowStepId =
  | "grab_image_source"
  | "turtlize_objects"
  | "run_prolog_checks"
  | "rule_induction"
  | "apply_rules_to_image"
  | "compare_artifacts"
  | "images_displayer"
  | "turtlized_objects_to_images"
  | "make_dataset"
  | "save_to_disk";

export type WorkflowStepStatus =
  | "idle"
  | "ready"
  | "running"
  | "completed"
  | "warning"
  | "failed";

export interface WorkflowStepDefinition {
  id: WorkflowStepId;
  order: number;
  title: string;
  shortTitle: string;
  description: string;
  consumes: DataType[];
  produces: DataType[];
}
