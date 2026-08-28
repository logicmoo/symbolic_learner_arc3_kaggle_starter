import { useEffect, useState } from "react";
import { GLOBAL_GENERATION_POLICIES, readGenerationParam, writeGenerationParam, type PageFamily } from "../lib/pageGenerations";
import { updateUserUiPreferences, useUserUiPreferences } from "../lib/uiPreferences";
import "../styles/page_generations.css";

/**
 * The page-history shell: renders one generation of a page family with a
 * stepper strip so the user can walk through every generation the page has
 * shipped.
 *
 * The generations notice has ONE view ladder, independent of which version
 * is shown: fullest (strip + provenance/policies) → full (strip) → compact
 * (titlebar chip) → gone. "Gone" flips the global preference, so the topbar
 * button switches to "Show Generations" — and showing again reopens the
 * notice in the fullest mode.
 */
export function GenerationHost({ family, workspaceId }: { family: PageFamily; workspaceId: string }) {
  const total = family.generations.length;
  const [generation, setGeneration] = useState(() => readGenerationParam(total));
  // The ONE shared view of the generations notice, persisted in the user
  // preference store — every page starts with whatever the previous page
  // left exposed. Ladder: fullest → full → compact → gone (global hide).
  const { generationsVisible, generationsView: view } = useUserUiPreferences();
  const setView = (next: "fullest" | "full" | "compact") => updateUserUiPreferences({ generationsView: next });
  useEffect(() => { writeGenerationParam(generation); }, [generation]);
  const active = family.generations[Math.min(total, Math.max(1, generation)) - 1];
  const Component = active.component;
  const policies = [...GLOBAL_GENERATION_POLICIES, ...(family.policies || [])];
  const allTheWayGone = () => updateUserUiPreferences({ generationsVisible: false });
  const reduce = () => {
    if (view === "fullest") setView("full");
    else if (view === "full") setView("compact");
    else allTheWayGone();
  };
  if (!generationsVisible) {
    return <div className="page-generations"><Component key={active.generation} workspaceId={workspaceId} /></div>;
  }
  return (
    <div className="page-generations">
      {view === "compact" ? (
        <div className="page-generations-strip is-compact" role="navigation" aria-label={`${family.title} generations`}>
          <button
            className="page-generations-chip"
            title={`${family.title} · ${active.note} — click to expand`}
            onClick={() => setView("full")}
          >
            {active.verdict === "red-herring" ? "⚠" : "★"} v{active.generation}/{total}
          </button>
          <button title="Reduce all the way: hide generations (the topbar switches to Show Generations)" onClick={allTheWayGone}>–</button>
        </div>
      ) : (
        <div className="page-generations-strip" role="navigation" aria-label={`${family.title} generations`}>
          <b>{family.title}</b>
          <div className="page-generations-steps">
            {family.generations.map((entry) => (
              <button
                key={entry.generation}
                className={`${entry.generation === active.generation ? "is-active" : ""}${entry.verdict === "red-herring" ? " is-red-herring" : ""}`}
                title={entry.verdict === "red-herring" ? `RED HERRING — do not study toward the next version. ${entry.lessons || entry.note}` : entry.note}
                onClick={() => setGeneration(entry.generation)}
              >
                {entry.verdict === "red-herring" ? "⚠ " : entry.verdict === "canonical" ? "★ " : ""}v{entry.generation} · {entry.label}
              </button>
            ))}
          </div>
          <button
            disabled={active.generation <= 1}
            title="Step back through this page's history"
            onClick={() => setGeneration(active.generation - 1)}
          >
            ← older
          </button>
          <button
            disabled={active.generation >= total}
            title="Step forward through this page's history"
            onClick={() => setGeneration(active.generation + 1)}
          >
            newer →
          </button>
          <button
            className={view === "fullest" ? "is-active" : ""}
            title="Provenance: how this generation was built, the policies, and where the next version goes"
            onClick={() => setView(view === "fullest" ? "full" : "fullest")}
          >
            ⓘ provenance
          </button>
          <button title={view === "fullest" ? "Reduce: hide the provenance panel" : "Reduce: shrink to a titlebar chip"} onClick={reduce}>–</button>
          <small title={active.note}>{active.generation}/{total}</small>
        </div>
      )}
      {view === "fullest" && (
        <div className="page-generations-provenance">
          <div>
            <b>GENERATION v{active.generation} · {active.label} · <span className={`verdict-${active.verdict}`}>{active.verdict.toUpperCase()}</span></b>
            {active.verdict === "red-herring" && (
              <p className="page-generations-warning">⚠ Recorded dead end — kept runnable for the history, but future versions must NOT study this design. Read the lessons instead.</p>
            )}
            <table>
              <tbody>
                <tr><td>component</td><td><code>{active.provenance.componentPath}</code></td></tr>
                <tr><td>built from</td><td><code>{active.provenance.builtFrom}</code></td></tr>
                {active.provenance.builtBy && <tr><td>built by</td><td>{active.provenance.builtBy}</td></tr>}
                {active.provenance.date && <tr><td>date</td><td>{active.provenance.date}</td></tr>}
                {active.provenance.nextVersionHint && <tr><td>next version</td><td>{active.provenance.nextVersionHint}</td></tr>}
                {active.lessons && <tr><td>lessons</td><td>{active.lessons}</td></tr>}
                <tr><td>note</td><td>{active.note}</td></tr>
              </tbody>
            </table>
          </div>
          <div>
            <b>POLICIES</b>
            <ol>
              {policies.map((policy, index) => (<li key={index}>{policy}</li>))}
            </ol>
          </div>
        </div>
      )}
      <Component key={active.generation} workspaceId={workspaceId} />
    </div>
  );
}
