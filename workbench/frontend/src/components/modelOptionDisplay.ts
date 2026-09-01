export type ModelOptionDisplayChoice = {
  id: string;
  label?: string;
  backendId?: string;
  backendLabel?: string;
  capabilities?: Record<string, unknown>;
};

const CAPABILITY_KEYS = [
  "multimodal",
  "vision",
  "imageOutput",
  "summary",
  "audio",
  "reasoning",
  "tools",
  "code",
  "json",
  "text",
] as const;

const normalizedName = (model: ModelOptionDisplayChoice) =>
  `${model.id} ${model.label || ""}`.toLowerCase();

export function modelCapabilityTags(model: ModelOptionDisplayChoice): string[] {
  const raw = model.capabilities || {};
  const capabilities: Record<(typeof CAPABILITY_KEYS)[number], boolean> = {
    multimodal: raw.multimodal === true,
    vision: raw.vision === true,
    imageOutput: raw.imageOutput === true || raw.imageGeneration === true,
    summary: raw.summary === true,
    audio: raw.audio === true,
    reasoning: raw.reasoning === true,
    tools: raw.tools === true,
    code: raw.code === true,
    json: raw.json === true,
    text: raw.text === true,
  };
  const name = normalizedName(model);
  if (/gemma[-_/](3|4)([^0-9]|$)/.test(name)) {
    Object.assign(capabilities, { vision: true, multimodal: true, text: true, reasoning: true });
  }
  if (/claude[-_/](3|3\.5|3\.7|4|5)/.test(name) || /claude[-_/](haiku|sonnet|opus)/.test(name)) {
    Object.assign(capabilities, { vision: true, multimodal: true, text: true });
  }
  return CAPABILITY_KEYS.filter((key) => capabilities[key]).map((key) => key === "imageOutput" ? "image output" : key);
}

export function modelOptionLabel(model: ModelOptionDisplayChoice): string {
  const tags = modelCapabilityTags(model);
  const suffix = tags.length ? ` [${tags.join(", ")}]` : "";
  return `${model.backendLabel || model.backendId || model.id} · ${model.label || model.id}${suffix}`;
}
