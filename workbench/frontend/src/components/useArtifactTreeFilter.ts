import { useEffect, useRef, useState } from "react";

export function useArtifactTreeFilter() {
  const treeRef = useRef<HTMLDivElement>(null);
  const [treeFilter, setTreeFilter] = useState("");
  const [showParents, setShowParents] = useState(false);

  useEffect(() => {
    const root = treeRef.current;
    if (!root) return;
    const query = treeFilter.trim().toLocaleLowerCase();
    root.classList.toggle("tree-filter-active", Boolean(query));
    const branches = Array.from(root.querySelectorAll<HTMLElement>(".operation-tree-group,.inheritance-node"));
    const leaves = Array.from(root.querySelectorAll<HTMLElement>(".operation-tree-row.operation-child"));
    const heads = branches.map(branch => branch.querySelector<HTMLElement>(":scope > .artifact-tree-branch-head") || branch.querySelector<HTMLElement>(":scope > .inheritance-row"));
    branches.forEach(branch => { branch.hidden = false; });
    heads.forEach(head => { if (head) head.hidden = false; });
    leaves.forEach(leaf => { leaf.hidden = false; });
    if (!query) return;

    leaves.forEach(leaf => { leaf.hidden = !String(leaf.textContent || "").toLocaleLowerCase().includes(query); });
    [...branches].reverse().forEach((branch, index) => {
      const head = heads[branches.length - index - 1];
      const summary = head?.querySelector<HTMLElement>(".artifact-tree-branch-summary") || head;
      const ownMatch = String(summary?.textContent || "").toLocaleLowerCase().includes(query);
      const childBranchMatch = Array.from(branch.querySelectorAll<HTMLElement>(":scope > .operation-tree-children > .operation-tree-group,:scope > .inheritance-children > .inheritance-node")).some(child => !child.hidden);
      const childLeafMatch = Array.from(branch.querySelectorAll<HTMLElement>(":scope > .operation-tree-children > .operation-child")).some(child => !child.hidden);
      branch.hidden = !(ownMatch || childBranchMatch || childLeafMatch);
      if (head) head.hidden = !ownMatch && !showParents;
    });
  }, [treeFilter, showParents]);

  return { treeRef, treeFilter, setTreeFilter, showParents, setShowParents };
}
