import { type ComponentType } from "react";

/**
 * Page generations: the page version-management system.
 *
 * A page family keeps every generation it has shipped (v1, v2, ...), each
 * one rebuilt from a written build prompt (see the page's help document).
 * The user can step through a page's history with the GenerationStepper;
 * `?gen=N` pins a generation in the URL. Any page can adopt this by
 * registering its generations here.
 *
 * Global policies (enforced by review, verified against the live app):
 * see GLOBAL_GENERATION_POLICIES below and
 * workbench/docs/design/PAGE_GENERATIONS.md.
 */
export const GLOBAL_GENERATION_POLICIES: readonly string[] = [
  "Never take away features: every new generation must be a superset of the one before it — the union of useful features, never the lowest common denominator.",
  "Every shipped generation stays runnable and steppable; upgrades add a generation, they never delete one.",
  "A new generation is constructed from the page's written build prompt (the help document's appendix), updated first to describe the target.",
  "Every generation records provenance — component path, build prompt, builder, date — so the next version knows exactly where and how to start.",
  "Consult each generation's verdict before studying it: build on 'canonical' generations; 'red-herring' generations are recorded dead ends — learn only their lessons, never their design.",
  "All displayed data comes from the real backend/filesystem; generations share the same backend contracts.",
];

/**
 * How the next builder should treat a generation:
 * - canonical: the current best — study and build on it.
 * - superseded: fine work, replaced by a newer canonical generation.
 * - experimental: promising but unproven — evaluate before adopting ideas.
 * - red-herring: a recorded dead end / bad idea. Keep it runnable for the
 *   history, but do NOT study its design toward the next version; read its
 *   `lessons` instead.
 */
export type GenerationVerdict = "canonical" | "superseded" | "experimental" | "red-herring";

export type GenerationProvenance = {
  /** Repository path of the React component implementing this generation. */
  componentPath: string;
  /** Repository path of the build prompt / help doc this generation was built from. */
  builtFrom: string;
  /** Who or what built it (a person, "copilot", a session name...). */
  builtBy?: string;
  /** ISO date the generation shipped. */
  date?: string;
  /** Where the next generation should be constructed. */
  nextVersionHint?: string;
};

export type PageGeneration = {
  /** 1-based generation number. */
  generation: number;
  label: string;
  /** What changed / why this generation exists. */
  note: string;
  /** How future builders should treat this generation. */
  verdict: GenerationVerdict;
  /** What was learned — REQUIRED reading when the verdict is red-herring. */
  lessons?: string;
  provenance: GenerationProvenance;
  component: ComponentType<{ workspaceId: string }>;
};

export type PageFamily = {
  family: string;
  title: string;
  /** Family-specific policies, appended to GLOBAL_GENERATION_POLICIES. */
  policies?: string[];
  generations: PageGeneration[];
};

export function readGenerationParam(total: number): number {
  const raw = new URLSearchParams(window.location.search).get("gen");
  const parsed = Number(raw);
  if (!raw || !Number.isFinite(parsed)) return total;
  return Math.max(1, Math.min(total, Math.round(parsed)));
}

export function writeGenerationParam(generation: number): void {
  const url = new URL(window.location.href);
  url.searchParams.set("gen", String(generation));
  window.history.replaceState(null, "", url.toString());
}
