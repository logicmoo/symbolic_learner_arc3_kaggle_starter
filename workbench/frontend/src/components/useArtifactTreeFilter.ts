import { useEffect, useRef, useState } from "react";

export type TreeVisibilityRule = "show" | "hide" | "unspecified";
export type TreeVisibilityRules = {
  search: TreeVisibilityRule;
  enabled: TreeVisibilityRule;
  disabled: TreeVisibilityRule;
  categories: TreeVisibilityRule;
  roles: Record<string, TreeVisibilityRule>;
};

export const DEFAULT_TREE_VISIBILITY_RULES: TreeVisibilityRules = {
  search: "unspecified",
  enabled: "unspecified",
  disabled: "unspecified",
  categories: "unspecified",
  roles: {},
};
const LEGACY_FILTERING_RULES: TreeVisibilityRules = { ...DEFAULT_TREE_VISIBILITY_RULES, search: "show" };
const TREE_ITEM_SELECTOR = ".operation-tree-group,.inheritance-node,.operation-tree-row.operation-child";

type BranchInfo = {
  element: HTMLElement;
  head: HTMLElement | null;
  parentElement: HTMLElement | null;
  kind: string | null;
  role: string;
  category: string | null;
  enabled: boolean;
  searchMatch: boolean;
  ownVisible: boolean;
};

function parsedSearchValue(element: HTMLElement): Record<string, unknown> {
  try {
    const parsed = JSON.parse(element.dataset.treeSearch || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed as Record<string, unknown> : {};
  } catch { return {}; }
}

function documentValue(value: Record<string, unknown>): Record<string, unknown> {
  const document = value.document;
  return document && typeof document === "object" && !Array.isArray(document) ? document as Record<string, unknown> : value;
}

function titleKind(value: string) { return value.replace(/[_-]+/g, " ").replace(/\b\w/g, letter => letter.toUpperCase()); }

function nestedKinds(value: unknown): string[] {
  if (!value || typeof value !== "object") return [];
  if (Array.isArray(value)) return value.flatMap(nestedKinds);
  const record = value as Record<string, unknown>;
  const document = documentValue(record);
  const ownKind = typeof document.kind === "string" ? [document.kind] : [];
  return [...ownKind, ...nestedKinds(record.children)];
}

function groupAllows(value: string, states: Record<string, TreeVisibilityRule>): boolean {
  if (states[value] === "hide") return false;
  const hasShow = Object.values(states).some(state => state === "show");
  return !hasShow || states[value] === "show";
}

export function useArtifactTreeFilter(rules?: TreeVisibilityRules) {
  const activeRules = rules || LEGACY_FILTERING_RULES;
  const treeRef = useRef<HTMLDivElement>(null);
  const [treeFilter, setTreeFilter] = useState("");
  const [showParents, setShowParents] = useState(false);
  const [treeKinds, setTreeKinds] = useState<string[]>([]);

  useEffect(() => {
    const root = treeRef.current;
    if (!root) return;
    const applyFilter = () => {
      const query = treeFilter.trim().toLocaleLowerCase();
      const branchElements = Array.from(root.querySelectorAll<HTMLElement>(TREE_ITEM_SELECTOR));
      const searchableData = (element?: HTMLElement | null) => {
        const source = element?.dataset.treeSearch || "";
        try {
          const parsed = JSON.parse(source);
          if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return source;
          const { children: _children, preferredChild: _preferredChild, ...ownFields } = parsed as Record<string, unknown>;
          return JSON.stringify(ownFields);
        } catch { return source; }
      };
      const searchableText = (element?: HTMLElement | null) => `${searchableData(element)} ${element?.textContent || ""}`.toLocaleLowerCase();
      const infos: BranchInfo[] = branchElements.map(element => {
        const raw = parsedSearchValue(element);
        const document = documentValue(raw);
        const category = typeof raw.category === "string" ? raw.category : null;
        const kind = category ? null : typeof document.kind === "string" ? document.kind : null;
        const head = element.matches(".operation-tree-row.operation-child") ? element : element.querySelector<HTMLElement>(":scope > .artifact-tree-branch-head") || element.querySelector<HTMLElement>(":scope > .inheritance-row");
        const parentElement = element.parentElement?.closest<HTMLElement>(TREE_ITEM_SELECTOR) || null;
        const parentRaw = parentElement ? parsedSearchValue(parentElement) : {};
        const parentDocument = documentValue(parentRaw);
        const parentKind = typeof parentDocument.kind === "string" ? parentDocument.kind : null;
        const role = kind ? `${parentKind === kind ? "child" : "top"}-${kind}` : "other";
        const enabled = !Boolean(head?.querySelector(".resource-disabled"));
        const searchMatch = Boolean(query) && `${searchableData(element).toLocaleLowerCase()} ${searchableText(head)}`.includes(query);
        return { element, head, parentElement, kind, role, category, enabled, searchMatch, ownVisible: true };
      });

      const kinds = [...new Set(branchElements.flatMap(element => nestedKinds(parsedSearchValue(element))))].sort();
      setTreeKinds(current => current.join("\u0000") === kinds.join("\u0000") ? current : kinds);
      const roleStates = { ...activeRules.roles };
      const availabilityStates = { enabled: activeRules.enabled, disabled: activeRules.disabled };
      const hasTypedRoles = Object.keys(roleStates).length > 0;

      for (const info of infos) {
        info.element.hidden = false;
        info.head?.removeAttribute("hidden");
        info.element.classList.remove("tree-search-match", "tree-structural-parent");
        if (info.searchMatch) info.element.classList.add("tree-search-match");
        if (info.category) {
          info.ownVisible = activeRules.categories !== "hide";
          if (activeRules.categories === "hide" && info.category === "all") info.ownVisible = false;
          if (activeRules.categories === "hide" && info.category !== "all") info.element.hidden = true;
          continue;
        }
        const availabilityVisible = groupAllows(info.enabled ? "enabled" : "disabled", availabilityStates);
        const roleVisible = groupAllows(info.role, hasTypedRoles ? roleStates : {});
        const searchVisible = !query || activeRules.search === "unspecified" || (activeRules.search === "show" ? info.searchMatch : !info.searchMatch);
        info.ownVisible = availabilityVisible && roleVisible && searchVisible;
      }

      const visibleDescendants = new Set<HTMLElement>();
      for (const info of [...infos].reverse()) {
        if (info.element.hidden) continue;
        const descendantVisible = visibleDescendants.has(info.element);
        if (!info.ownVisible && !descendantVisible) {
          info.element.hidden = true;
          continue;
        }
        if (info.parentElement) visibleDescendants.add(info.parentElement);
        if (!info.ownVisible && info.head) {
          info.head.hidden = !showParents;
          if (showParents) info.element.classList.add("tree-structural-parent");
        }
      }

      root.classList.toggle("tree-filter-active", Boolean(query) && activeRules.search === "show");
      root.classList.toggle("tree-filter-show-parents", Boolean(query) && showParents);
      root.classList.toggle("tree-visibility-active", [...Object.values(activeRules).filter(value => typeof value === "string"), ...Object.values(activeRules.roles)].some(value => value === "show" || value === "hide"));
      root.dataset.treeKinds = kinds.map(titleKind).join(", ");
    };
    applyFilter();
    const observer = new MutationObserver(applyFilter);
    observer.observe(root, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [treeFilter, showParents, activeRules]);

  return { treeRef, treeFilter, setTreeFilter, showParents, setShowParents, treeKinds };
}
