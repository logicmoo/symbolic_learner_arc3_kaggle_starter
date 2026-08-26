import { OperationPlayground } from "./OperationPlayground";
import { relationshipIds, specializationInheritanceMap, specializesResource } from "./resourceRelationships";
import { jsonValueToMetta } from "../lib/mettaResourceCodec";

export type ModelStrategy = "single" | "parallel" | "compare" | "fallback";

export type OperationDef = {
  kind: "operation";
  id: string;
  implements?: Record<string, unknown>;
  label?: string;
  description?: string;
  categories?: string[];
  topics?: string[];
  enabled?: boolean;
  role?: string;
  implementation?: string;
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  specializations?: Record<string, unknown>;
  preferredSpecialization?: string;
};

export type OperationImplementationDef = {
  kind: "operation";
  id: string;
  implements: Record<string, unknown>;
  label?: string;
  description?: string;
  categories?: string[];
  topics?: string[];
  enabled?: boolean;
  implementation: string;
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  parameters?: Record<string, unknown>;
  bindings?: Record<string, unknown>;
  python?: Record<string, unknown>;
  prolog?: Record<string, unknown>;
  metta?: Record<string, unknown>;
  modelSelection?: { models?: string[]; strategy?: ModelStrategy };
};

export type OperationResource = OperationDef | OperationImplementationDef;

export type OperationModelChoice = {
  id: string;
  label?: string;
  kind?: string;
  model?: string;
  enabled?: boolean;
};

export type OperationPromptChoice = {
  id: string;
  label?: string;
  description?: string;
};

export type OperationPromptProfileChoice = OperationPromptChoice & {
  prompts: string[];
};

export type OperationSuperControlRequest = {
  kind: "operation";
  workspaceId: string;
  source: string;
  sourceScope: string;
  path: string;
  dirty: boolean;
  secondary: boolean;
  busy: boolean;
  variants: OperationImplementationDef[];
  implementedOperation?: OperationDef | null;
  relatedResources: OperationResource[];
  models: OperationModelChoice[];
  prompts: OperationPromptChoice[];
  promptProfiles: OperationPromptProfileChoice[];
  onChange: (value: string) => void;
  onSave: () => void;
  onToggleEnabled?: () => void;
  onCreateSpecialization?: () => void;
};

export function parseOperationResource(source: string): OperationResource | null {
  try {
    return source ? JSON.parse(source) as OperationResource : null;
  } catch {
    return null;
  }
}

export function describeOperationDocument(source: string, fallback: string) {
  const document = parseOperationResource(source);
  const isImplementation = Boolean(document && relationshipIds(document.implements).length);
  return {
    document,
    isImplementation,
    tabLabel: isImplementation ? "OPERATION IMPLEMENTATION" : "ABSTRACT OPERATION",
    title: document?.label || document?.id || fallback,
  };
}

export function OperationDocumentControl({ request }: { request: OperationSuperControlRequest }) {
  const document = parseOperationResource(request.source);
  const isImplementation = Boolean(document && relationshipIds(document.implements).length);
  const abstract = document && !isImplementation ? document as OperationDef : null;
  const selectedImplementation = document && isImplementation ? document as OperationImplementationDef : null;
  const selectedModels = selectedImplementation?.modelSelection?.models || [];
  const implementationBindings = (selectedImplementation?.bindings || {}) as Record<string, unknown>;
  const selectedPrompts = Array.isArray(implementationBindings.prompts)
    ? implementationBindings.prompts as string[]
    : [];
  const selectedPromptProfiles = Array.isArray(implementationBindings.promptProfiles)
    ? implementationBindings.promptProfiles as string[]
    : implementationBindings.promptProfile
      ? [String(implementationBindings.promptProfile)]
      : [];
  const directRoute = abstract?.implementation && request.variants.length === 0
    ? abstract.implementation
    : null;

  const patchAbstract = (patch: Partial<OperationDef>) => {
    if (abstract) request.onChange(JSON.stringify({ ...abstract, ...patch }, null, 2));
  };
  const setDefaultImplementation = (id: string) => {
    if (!abstract) return;
    const declared = specializationInheritanceMap(abstract.specializations);
    const specializations = Object.keys(declared).length
      ? declared
      : Object.assign({}, ...request.variants.map(variant => specializesResource(variant.id)));
    patchAbstract({ preferredSpecialization: id || undefined, specializations });
  };
  const patchImplementation = (patch: Partial<OperationImplementationDef>) => {
    if (selectedImplementation) request.onChange(JSON.stringify({ ...selectedImplementation, ...patch }, null, 2));
  };
  const toggleModel = (id: string) => {
    if (!selectedImplementation) return;
    const models = selectedModels.includes(id)
      ? selectedModels.filter(modelId => modelId !== id)
      : [...selectedModels, id];
    patchImplementation({
      modelSelection: {
        models,
        strategy: selectedImplementation.modelSelection?.strategy || "single",
      },
    });
  };
  const updatePrompts = (ids: string[]) => {
    if (!selectedImplementation) return;
    patchImplementation({
      bindings: {
        ...(selectedImplementation.bindings || {}),
        prompts: ids,
        separator: selectedImplementation.bindings?.separator || "\n\n",
      },
    });
  };
  const togglePrompt = (id: string) => {
    updatePrompts(selectedPrompts.includes(id)
      ? selectedPrompts.filter(promptId => promptId !== id)
      : [...selectedPrompts, id]);
  };
  const togglePromptProfile = (id: string) => {
    if (!selectedImplementation) return;
    const promptProfiles = selectedPromptProfiles.includes(id)
      ? selectedPromptProfiles.filter(profileId => profileId !== id)
      : [...selectedPromptProfiles, id];
    const bindings: Record<string, unknown> = {
      ...(selectedImplementation.bindings || {}),
      promptProfiles,
    };
    delete bindings.promptProfile;
    patchImplementation({ bindings });
  };
  const movePrompt = (index: number, delta: number) => {
    const next = [...selectedPrompts];
    const destination = index + delta;
    if (destination < 0 || destination >= next.length) return;
    [next[index], next[destination]] = [next[destination], next[index]];
    updatePrompts(next);
  };

  return <div className="operation-editor-scroll operation-document-sub-control">
    {!document && <div className="demo-notice"><b>Invalid resource</b><span>Fix the source before saving this resource.</span></div>}
    {abstract && <>
      <div className="operation-abstract-summary">
        <div><span>ROLE</span><b>{abstract.role || "abstract_stage"}</b></div>
        <div>
          <span>DEFAULT IMPLEMENTATION</span>
          <select
            value={directRoute ? abstract.id : abstract.preferredSpecialization || ""}
            disabled={Boolean(directRoute)}
            onChange={event => setDefaultImplementation(event.target.value)}
          >
            {directRoute
              ? <option value={abstract.id}>Direct — {directRoute}</option>
              : <option value="">planner-selected</option>}
            {request.variants.map(implementation => {
              const language = implementation.implementation.startsWith("python")
                ? "Python"
                : implementation.implementation.startsWith("prolog")
                  ? "Prolog"
                  : implementation.implementation.startsWith("metta")
                    ? "MeTTa"
                    : implementation.implementation.startsWith("llm")
                      ? "LLM"
                      : "Implementation";
              return <option key={implementation.id} value={implementation.id}>
                {language} — {implementation.label || implementation.id}
              </option>;
            })}
          </select>
        </div>
        <div><span>INPUTS</span><code>{Object.keys(abstract.inputs || {}).join(", ") || "—"}</code></div>
        <div><span>OUTPUTS</span><code>{Object.keys(abstract.outputs || {}).join(", ") || "—"}</code></div>
      </div>
      <OperationPlayground
        workspaceId={request.workspaceId}
        operation={abstract}
        variants={request.variants}
        models={request.models.map(model => ({ id: model.id, label: model.label, enabled: model.enabled }))}
        onDefaultImplementationChange={setDefaultImplementation}
      />
    </>}
    {selectedImplementation && <div className="implementation-summary">
      <div><span>ROUTE</span><b>{selectedImplementation.implementation}</b></div>
      <div><span>IMPLEMENTS</span><b>{relationshipIds(selectedImplementation.implements).join(", ")}</b></div>
      {selectedImplementation.python && <div className="wide">
        <span>PYTHON SOURCE</span>
        <code>
          {String(selectedImplementation.python.module || selectedImplementation.python.file || "configured source")}
          {selectedImplementation.python.className ? ` · ${String(selectedImplementation.python.className)}` : ""}
          {selectedImplementation.python.callable ? ` :: ${String(selectedImplementation.python.callable)}` : ""}
        </code>
      </div>}
      {selectedImplementation.prolog && <div className="wide">
        <span>SWI-PROLOG SOURCE</span>
        <code>{String(selectedImplementation.prolog.predicate || "predicate")} / {String(selectedImplementation.prolog.arity || "?")}</code>
      </div>}
      {selectedImplementation.metta && <div className="wide">
        <span>METTA SOURCE</span>
        <code>{jsonValueToMetta(selectedImplementation.metta)}</code>
      </div>}
    </div>}
    {selectedImplementation && request.implementedOperation && <OperationPlayground
      key={`${request.implementedOperation.id}:${selectedImplementation.id}`}
      workspaceId={request.workspaceId}
      operation={request.implementedOperation}
      variants={[selectedImplementation]}
      models={request.models.map(model => ({ id: model.id, label: model.label, enabled: model.enabled }))}
    />}
    {selectedImplementation?.implementation.startsWith("llm") && request.promptProfiles.length > 0 && <div className="operation-llm-config">
      <div className="llm-subhead"><div><span>PROMPT PROFILES</span><b>Reusable ordered prompt compositions, independent of the selected model or preset</b></div></div>
      <div className="operation-model-list compact">
        {request.promptProfiles.map(profile => {
          const checked = selectedPromptProfiles.includes(profile.id);
          return <label className={`operation-model-option ${checked ? "selected" : ""}`} key={profile.id}>
            <input type="checkbox" checked={checked} onChange={() => togglePromptProfile(profile.id)} />
            <span><b>{profile.label || profile.id}</b><small>{profile.prompts.length} prompts · {profile.description || profile.id}</small></span>
          </label>;
        })}
      </div>
    </div>}
    {selectedImplementation?.implementation.startsWith("llm") && <div className="operation-llm-config">
      <div className="llm-subhead"><div><span>MODEL / PRESET DISPATCH</span><b>Models and reusable invocation presets allowed for this implementation</b></div></div>
      <div className="operation-model-list compact">
        {request.models.map(model => {
          const checked = selectedModels.includes(model.id);
          return <label className={`operation-model-option ${checked ? "selected" : ""}`} key={model.id}>
            <input type="checkbox" checked={checked} onChange={() => toggleModel(model.id)} />
            <span><b>{model.label || model.id}</b><small>{model.kind || "model"} · {model.model || "inherited model"}</small></span>
          </label>;
        })}
      </div>
      <div className="llm-subhead"><div><span>PROMPT COMPOSITION</span><b>Ordered prompts used by this implementation</b></div></div>
      <div className="operation-model-list compact">
        {request.prompts.map(prompt => {
          const checked = selectedPrompts.includes(prompt.id);
          const index = selectedPrompts.indexOf(prompt.id);
          return <div className={`operation-model-option ${checked ? "selected" : ""}`} key={prompt.id}>
            <input type="checkbox" checked={checked} onChange={() => togglePrompt(prompt.id)} />
            <span><b>{prompt.label || prompt.id}</b><small>{prompt.description || prompt.id}</small></span>
            {checked && <em>
              <button onClick={() => movePrompt(index, -1)} disabled={index === 0}>↑</button>
              {" "}{index + 1}{" "}
              <button onClick={() => movePrompt(index, 1)} disabled={index === selectedPrompts.length - 1}>↓</button>
            </em>}
          </div>;
        })}
      </div>
    </div>}
  </div>;
}
