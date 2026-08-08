import { useEffect, useRef, useState } from "react";

export function useArtifactTreeFilter() {
  const treeRef = useRef<HTMLDivElement>(null);
  const [treeFilter, setTreeFilter] = useState("");
  const [showParents, setShowParents] = useState(false);

  useEffect(() => {
    const root = treeRef.current;
    if (!root) return;
    const applyFilter = () => {
      const query = treeFilter.trim().toLocaleLowerCase();
      root.classList.toggle("tree-filter-active", Boolean(query));
      root.classList.toggle("tree-filter-show-parents", Boolean(query) && showParents);
      const branches = Array.from(root.querySelectorAll<HTMLElement>(".operation-tree-group,.inheritance-node"));
      const leaves = Array.from(root.querySelectorAll<HTMLElement>(".operation-tree-row.operation-child"));
      const heads = branches.map(branch => branch.querySelector<HTMLElement>(":scope > .artifact-tree-branch-head") || branch.querySelector<HTMLElement>(":scope > .inheritance-row"));
      branches.forEach(branch => { branch.hidden = false; delete branch.dataset.filterOwnMatch; });
      heads.forEach(head => { if (head) head.hidden = false; });
      leaves.forEach(leaf => { leaf.hidden = false; });
      if (!query) return;

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
      leaves.forEach(leaf => { leaf.hidden = !searchableText(leaf).includes(query); });
      [...branches].reverse().forEach((branch, index) => {
        const head = heads[branches.length - index - 1];
        const summary = head?.querySelector<HTMLElement>(".artifact-tree-branch-summary") || head;
        const ownMatch = `${searchableData(branch).toLocaleLowerCase()} ${searchableText(summary)}`.includes(query);
        const childBranchMatch = Array.from(branch.querySelectorAll<HTMLElement>(":scope > .operation-tree-children > .operation-tree-group,:scope > .inheritance-children > .inheritance-node")).some(child => !child.hidden);
        const childLeafMatch = Array.from(branch.querySelectorAll<HTMLElement>(":scope > .operation-tree-children > .operation-child")).some(child => !child.hidden);
        branch.hidden = !(ownMatch || childBranchMatch || childLeafMatch);
        branch.dataset.filterOwnMatch = ownMatch ? "true" : "false";
        if (head) head.hidden = !ownMatch && !showParents;
      });
    };
    applyFilter();
    const observer = new MutationObserver(applyFilter);
    observer.observe(root, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [treeFilter, showParents]);

  return { treeRef, treeFilter, setTreeFilter, showParents, setShowParents };
}
