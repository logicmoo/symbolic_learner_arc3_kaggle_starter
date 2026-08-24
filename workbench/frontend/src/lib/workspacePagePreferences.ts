import { useSyncExternalStore } from "react";

const STORAGE_KEY = "metta-workbench.workspace-page-preferences.v1";
const CHANGE_EVENT = "workbench:workspace-page-preferences-changed";

export type WorkspaceOpeningPage = "last" | string;

type WorkspacePagePreferences = {
  openingPageByWorkspace: Record<string, WorkspaceOpeningPage>;
  lastPageByWorkspace: Record<string, string>;
  systemOpeningPage: string;
};

const EMPTY_PREFERENCES: WorkspacePagePreferences = {
  openingPageByWorkspace: {},
  lastPageByWorkspace: {},
  systemOpeningPage: "overview",
};

let cachedSource = "";
let cachedPreferences = EMPTY_PREFERENCES;

const readPreferences = (): WorkspacePagePreferences => {
  if (typeof window === "undefined") return EMPTY_PREFERENCES;
  const source = window.localStorage.getItem(STORAGE_KEY) || "";
  if (source === cachedSource) return cachedPreferences;
  cachedSource = source;
  try {
    const parsed = JSON.parse(source) as Partial<WorkspacePagePreferences>;
    cachedPreferences = {
      openingPageByWorkspace: parsed.openingPageByWorkspace || {},
      lastPageByWorkspace: parsed.lastPageByWorkspace || {},
      systemOpeningPage: parsed.systemOpeningPage || "overview",
    };
  } catch {
    cachedPreferences = EMPTY_PREFERENCES;
  }
  return cachedPreferences;
};

const writePreferences = (preferences: WorkspacePagePreferences) => {
  const source = JSON.stringify(preferences);
  cachedSource = source;
  cachedPreferences = preferences;
  window.localStorage.setItem(STORAGE_KEY, source);
  window.dispatchEvent(new Event(CHANGE_EVENT));
};

const subscribe = (listener: () => void) => {
  window.addEventListener(CHANGE_EVENT, listener);
  window.addEventListener("storage", listener);
  return () => {
    window.removeEventListener(CHANGE_EVENT, listener);
    window.removeEventListener("storage", listener);
  };
};

export const useWorkspacePagePreferences = () =>
  useSyncExternalStore(subscribe, readPreferences, () => EMPTY_PREFERENCES);

export const setWorkspaceOpeningPage = (
  workspaceId: string,
  openingPage: WorkspaceOpeningPage,
) => {
  const current = readPreferences();
  writePreferences({
    ...current,
    openingPageByWorkspace: {
      ...current.openingPageByWorkspace,
      [workspaceId]: openingPage,
    },
  });
};

export const setSystemOpeningPage = (openingPage: string) => {
  const current = readPreferences();
  writePreferences({ ...current, systemOpeningPage: openingPage });
};

export const rememberWorkspaceLastPage = (workspaceId: string, page: string) => {
  const current = readPreferences();
  if (current.lastPageByWorkspace[workspaceId] === page) return;
  writePreferences({
    ...current,
    lastPageByWorkspace: {
      ...current.lastPageByWorkspace,
      [workspaceId]: page,
    },
  });
};

export const resolveWorkspaceOpeningPage = (
  workspaceId: string,
  inheritedWorkspaceIds: string[] = [],
) => {
  const preferences = readPreferences();
  const configured = preferences.openingPageByWorkspace[workspaceId];
  if (configured && configured !== "last" && configured !== "inherit") return configured;
  const lastPage = preferences.lastPageByWorkspace[workspaceId];
  if ((!configured || configured === "inherit" || configured === "last") && lastPage) return lastPage;
  for (const inheritedWorkspaceId of [...inheritedWorkspaceIds].reverse()) {
    const inherited = preferences.openingPageByWorkspace[inheritedWorkspaceId];
    if (inherited && inherited !== "last" && inherited !== "inherit") return inherited;
  }
  return preferences.systemOpeningPage || "overview";
};

export const WORKSPACE_OPENING_PAGE_OPTIONS = [
  { value: "inherit", label: "Automatic: Last Page, then Inherited / System" },
  { value: "last", label: "Last Page (then Inherited / System)" },
  { value: "overview", label: "Overview" },
  { value: "canvas", label: "Workflow Canvas" },
  { value: "currentWorkflow", label: "Current Workflow" },
  { value: "workflowPageBuilder", label: "Page Builder" },
  { value: "chat", label: "Chat" },
  { value: "goals", label: "Goals" },
  { value: "plans", label: "Planning" },
  { value: "operations", label: "Operations" },
  { value: "sourceCode", label: "Source Code" },
  { value: "systems", label: "Systems" },
  { value: "llms", label: "Models" },
  { value: "data", label: "Datatypes" },
  { value: "knowledgeData", label: "Data" },
  { value: "atomspaces", label: "AtomSpaces" },
  { value: "knowledgeArtifacts", label: "Artifacts" },
  { value: "goalRuns", label: "Goal Runs" },
  { value: "execs", label: "Executions" },
  { value: "events", label: "Events" },
  { value: "states", label: "States" },
  { value: "logs", label: "Logs" },
  { value: "setup", label: "Settings" },
] as const;
