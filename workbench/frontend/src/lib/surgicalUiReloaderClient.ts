import { markAllWorkbenchPageSessionsForRestart } from "./pageSessionState";
import { failUiRestart, onUIRestart, permitUiReload } from "./uiRestartLifecycle";

type SurgicalUiChange = { file?: string; changedAt?: string };

let handlingChange = false;

if (import.meta.hot) {
  import.meta.hot.on("workbench:surgical-ui-change", async (_change: SurgicalUiChange) => {
    if (handlingChange) return;
    handlingChange = true;
    let token = "";
    try {
      const parameters = new URLSearchParams(window.location.search);
      const restart = await onUIRestart({
        reason: "development-reload",
        workspaceId: parameters.get("workspace")?.trim() || "workspace-chooser",
        pageId: parameters.get("view")?.trim() || parameters.get("menu")?.trim() || "workspace-chooser",
        href: window.location.href,
      });
      token = restart.token;
      markAllWorkbenchPageSessionsForRestart(restart.requestedAt);
      if (!permitUiReload(restart.token)) throw new Error("Surgical UI reload was rejected as duplicate or stale.");
      window.location.reload();
    } catch (reason) {
      if (token) failUiRestart(token, reason);
      handlingChange = false;
      console.error("Surgical UI reload failed", reason);
    }
  });
}

