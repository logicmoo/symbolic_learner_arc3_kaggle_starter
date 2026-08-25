export interface CollabEvent {
  id: string;
  stream: string;
  seq: number;
  type: string;
  ts: string;
  source_id?: string;
  source_kind?: string;
  data?: Record<string, unknown>;
}

export interface Capabilities {
  product?: string;
  streams?: Record<string, string>;
  boot_id?: string;
}

export type Format = "markdown" | "json" | "metta" | "text";
export type ViewMode = "list" | "tiles";
