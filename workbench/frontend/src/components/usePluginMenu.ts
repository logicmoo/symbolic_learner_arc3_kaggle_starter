import { useCallback, useEffect, useState } from "react";

export type PluginMenuEntry = {
  pluginId: string;
  pluginLabel: string;
  id: string;
  label: string;
  kind: string;
  group: string;
  glyph: string;
  /** Address the desktop UI opens: an absolute page URL, or an API descriptor path. */
  address: string;
  external: boolean;
  declaredDescriptor: string;
  available: boolean;
};

type PluginUiPage = {
  id: string;
  label: string;
  kind: string;
  group?: string;
  glyph?: string;
  descriptor: string;
  address?: string;
  apiDescriptor?: string;
  external?: boolean;
};

type PluginRecord = {
  id: string;
  label?: string;
  loaded: boolean;
  uiPages?: PluginUiPage[];
};

/** Menu entries installed by the loaded plugins, resolved by each plugin. */
export function usePluginMenu() {
  const [entries, setEntries] = useState<PluginMenuEntry[]>([]);

  const load = useCallback(async () => {
    try {
      const response = await fetch("/workbench/plugins");
      if (!response.ok) return;
      const payload = (await response.json()) as { plugins: PluginRecord[] };
      setEntries(
        (payload.plugins || []).flatMap((plugin) =>
          (plugin.uiPages || []).map((page) => ({
            pluginId: plugin.id,
            pluginLabel: plugin.label || plugin.id,
            id: page.id,
            label: page.label,
            kind: page.kind,
            group: page.group || "PLUGINS",
            glyph: page.glyph || "⬡",
            address: page.address || page.apiDescriptor || page.descriptor,
            external: Boolean(page.external),
            declaredDescriptor: page.descriptor,
            available: plugin.loaded,
          })),
        ),
      );
    } catch {
      // The Plugins page reports catalog failures; the menu just stays empty.
    }
  }, []);

  useEffect(() => {
    void load();
    const refresh = () => void load();
    window.addEventListener("workbench:plugins-changed", refresh);
    return () => window.removeEventListener("workbench:plugins-changed", refresh);
  }, [load]);

  return { pluginMenu: entries, reloadPluginMenu: load };
}
