import { VideoImportPage, type VideoImportChainSummaryStep } from "./VideoImportPage";
import { GenerationHost } from "./GenerationHost";
import type { PageFamily } from "../lib/pageGenerations";

/**
 * The Video Import page family ? the first page on the upgrade system.
 *
 * GRADUATION (2026-08-29): the from-prompt rebuild proved itself and became
 * the family baseline ? v1. This reset the family epoch: the pre-graduation
 * organic build is removed (it lives in git history). Each generation was (re)built from the written build
 * prompt in workbench/docs/VIDEO_IMPORT.md; `?gen=N` pins one.
 */
const family: PageFamily = {
  family: "videoImport",
  title: "VIDEO IMPORT",
  policies: [
    "The input frames grid is never altered by a run; outputs are always copies.",
    "Every long-running step is interruptible (? Stop) with partial results kept.",
  ],
  generations: [
    {
      generation: 1,
      label: "organic",
      note: "The baseline. Graduated from the from-prompt rebuild (one API layer, one job engine, one stack runner, uniform collapsible sections) and now evolves organically in place: the pick?apply-to-all?re-base loop, let-USER-decide selectors, exact-state snapshot/restore, and split auto-clear toggles all grew here.",
      verdict: "canonical",
      lessons: "Its pre-graduation ancestor (the original organic build, now only in git history) scattered concerns ? three vote paths, two strip renders, ad-hoc section shells; the prompt rebuild consolidated them and then took over as baseline under the VideoImportPage.tsx name.",
      provenance: {
        componentPath: "workbench/frontend/src/components/VideoImportPage.tsx",
        builtFrom: "workbench/docs/VIDEO_IMPORT.md (appendix build prompt)",
        builtBy: "copilot session: Video import pipeline",
        date: "2026-08-29",
        nextVersionHint: "v2 (when it comes): update the build prompt first, register the new component here, never remove features (see PAGE_GENERATIONS.md)",
      },
      component: VideoImportPage,
    },
  ],
};

export function VideoImportFamily({
  workspaceId,
  onChainSummaryChange,
}: {
  workspaceId: string;
  onChainSummaryChange?: (steps: VideoImportChainSummaryStep[]) => void;
}) {
  return (
    <GenerationHost
      family={family}
      workspaceId={workspaceId}
      extraProps={onChainSummaryChange ? { onChainSummaryChange } : undefined}
    />
  );
}
