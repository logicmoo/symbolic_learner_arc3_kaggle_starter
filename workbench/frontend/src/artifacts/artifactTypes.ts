export type ArtifactId = string;

export type SemanticType =
  | "knowledge_artifact"
  | "individual_object"
  | "scene"
  | "transformation"
  | "program"
  | "rule"
  | "evidence"
  | "evaluation"
  | "provenance"
  | "dataset_bundle";

export type DataType =
  | "image"
  | "video"
  | "frame_sequence"
  | "image_set"
  | "turtle_program"
  | "turtle_drawing"
  | "prolog_facts"
  | "prolog_program"
  | "python_script"
  | "json"
  | "csv"
  | "text"
  | "markdown"
  | "prompt"
  | "object_annotation"
  | "bounding_box"
  | "mask"
  | "graph"
  | "change_description"
  | "rule_set"
  | "score"
  | "arc3_state"
  | "configuration"
  | "execution_log"
  | "artifact_bundle"
  | "provenance_record"
  | "file_reference";

export interface ArtifactReference {
  artifactId: ArtifactId;
  relationship:
    | "contains"
    | "derived_from"
    | "converted_from"
    | "references"
    | "evaluates"
    | "explains";
}

export interface ArtifactProvenance {
  source?: string;
  creator?: string;
  tool?: string;
  model?: string;
  createdAt: string;
  parentArtifactIds?: ArtifactId[];
}

export interface Artifact<T = unknown> {
  id: ArtifactId;
  name: string;
  semanticTypes: SemanticType[];
  dataType: DataType;
  payload: T;
  metadata: Record<string, unknown>;
  references: ArtifactReference[];
  provenance: ArtifactProvenance;
}

export interface ArcObject {
  id: string;
  name: string;
  color: number;
  cells: Array<[number, number]>;
  properties: Record<string, string | number | boolean>;
  turtleProgram: string;
  prologFacts: string;
  confidence: number;
}
