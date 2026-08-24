import { useSyncExternalStore } from "react";

export type ResourceSourceFileControlsPlacement = "above" | "below";

export type UserUiPreferences = {
  resourceSourceFileControlsPlacement: ResourceSourceFileControlsPlacement;
};

export const USER_UI_PREFERENCES_STORAGE_KEY = "metta-workbench.user-ui-preferences.v1";
export const USER_UI_PREFERENCES_CHANGED_EVENT = "workbench:user-ui-preferences-changed";

export const DEFAULT_USER_UI_PREFERENCES: UserUiPreferences = {
  resourceSourceFileControlsPlacement: "above",
};

let cachedSource: string | null | undefined;
let cachedPreferences = DEFAULT_USER_UI_PREFERENCES;

function parseUserUiPreferences(source: string | null): UserUiPreferences {
  if (!source) return DEFAULT_USER_UI_PREFERENCES;
  try {
    const candidate = JSON.parse(source) as Partial<UserUiPreferences>;
    return {
      resourceSourceFileControlsPlacement:
        candidate.resourceSourceFileControlsPlacement === "below" ? "below" : "above",
    };
  } catch {
    return DEFAULT_USER_UI_PREFERENCES;
  }
}

export function readUserUiPreferences(): UserUiPreferences {
  if (typeof window === "undefined") return DEFAULT_USER_UI_PREFERENCES;
  const source = window.localStorage.getItem(USER_UI_PREFERENCES_STORAGE_KEY);
  if (source !== cachedSource) {
    cachedSource = source;
    cachedPreferences = parseUserUiPreferences(source);
  }
  return cachedPreferences;
}

export function writeUserUiPreferences(preferences: UserUiPreferences): void {
  if (typeof window === "undefined") return;
  const source = JSON.stringify(preferences);
  window.localStorage.setItem(USER_UI_PREFERENCES_STORAGE_KEY, source);
  cachedSource = source;
  cachedPreferences = preferences;
  window.dispatchEvent(new CustomEvent(USER_UI_PREFERENCES_CHANGED_EVENT));
}

export function updateUserUiPreferences(patch: Partial<UserUiPreferences>): void {
  writeUserUiPreferences({ ...readUserUiPreferences(), ...patch });
}

function subscribeUserUiPreferences(listener: () => void): () => void {
  if (typeof window === "undefined") return () => undefined;
  const onStorage = (event: StorageEvent) => {
    if (!event.key || event.key === USER_UI_PREFERENCES_STORAGE_KEY) listener();
  };
  window.addEventListener("storage", onStorage);
  window.addEventListener(USER_UI_PREFERENCES_CHANGED_EVENT, listener);
  return () => {
    window.removeEventListener("storage", onStorage);
    window.removeEventListener(USER_UI_PREFERENCES_CHANGED_EVENT, listener);
  };
}

export function useUserUiPreferences(): UserUiPreferences {
  return useSyncExternalStore(subscribeUserUiPreferences, readUserUiPreferences, () => DEFAULT_USER_UI_PREFERENCES);
}
