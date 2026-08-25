import { createContext, lazy, Suspense, useContext, type ReactNode } from "react";
import type { SubControlDescriptor } from "../lib/subControls";

/**
 * Renderers for the Super Control's sub-control tabs.
 *
 * `subControls.ts` enumerates which tabs exist; this maps an enumerated id to
 * the control that draws it. A sub-control the registry does not know yet still
 * gets a tab, so the enumeration stays the single source of truth and wiring can
 * land progressively (see editor_consolidation_plan.md).
 */

/** What a sub-control needs to draw itself, independent of the host page. */
export type SubControlContextValue = {
  workspaceId?: string;
  /** Key of the artifact the host currently has active, when it has one. */
  activeKey?: string | null;
  /** Label of that artifact, for controls that only need to name it. */
  activeLabel?: string | null;
};

const SubControlContext = createContext<SubControlContextValue>({});
export const SubControlProvider = SubControlContext.Provider;
export const useSubControlContext = () => useContext(SubControlContext);

/**
 * Nesting depth of Super Controls.
 *
 * A sub-control may itself be a page built on the Super Control, so rendering
 * the tab strip unconditionally would recurse forever. Only the outermost Super
 * Control draws the strip; nested ones render their host body alone.
 */
const SuperControlDepthContext = createContext(0);
export const SuperControlDepthProvider = SuperControlDepthContext.Provider;
export const useSuperControlDepth = () => useContext(SuperControlDepthContext);

const OperationLibraryEditor = lazy(() =>
  import("./OperationLibraryEditor").then(module => ({ default: module.OperationLibraryEditor })),
);
const PromptLibraryEditor = lazy(() =>
  import("./PromptLibraryEditor").then(module => ({ default: module.PromptLibraryEditor })),
);
const DataCatalogPanel = lazy(() =>
  import("./DataCatalogPanel").then(module => ({ default: module.DataCatalogPanel })),
);
const LlmModelsEditor = lazy(() =>
  import("./LlmModelsEditor").then(module => ({ default: module.LlmModelsEditor })),
);

type SubControlRenderer = (context: SubControlContextValue) => ReactNode;

const RENDERERS: Record<string, SubControlRenderer> = {
  "operation-library": context =>
    context.workspaceId ? <OperationLibraryEditor workspaceId={context.workspaceId} /> : null,
  "prompt-library": context =>
    context.workspaceId ? <PromptLibraryEditor workspaceId={context.workspaceId} /> : null,
  "data-catalog": context =>
    context.workspaceId ? <DataCatalogPanel workspaceId={context.workspaceId} /> : null,
  "models": context =>
    context.workspaceId ? <LlmModelsEditor workspaceId={context.workspaceId} /> : null,
};

export function hasSubControlRenderer(id: string): boolean {
  return Boolean(RENDERERS[id]);
}

/** Draw one enumerated sub-control, or explain that it is not wired yet. */
export function SubControlBody({ descriptor }: { descriptor: SubControlDescriptor }) {
  const context = useSubControlContext();
  const renderer = RENDERERS[descriptor.id];
  if (!renderer) {
    return <div className="studio-empty sub-control-pending">
      <b>{descriptor.label}</b>
      <span>This surface is enumerated but not wired into the Super Control yet.</span>
    </div>;
  }
  const body = renderer(context);
  if (body === null) {
    return <div className="studio-empty sub-control-pending">
      <b>{descriptor.label}</b>
      <span>Needs a workspace; open this from a workspace page.</span>
    </div>;
  }
  return <Suspense fallback={<div className="studio-empty">Loading {descriptor.label}…</div>}>{body}</Suspense>;
}
