import { Children, Fragment, isValidElement, useMemo, type ReactElement, type ReactNode } from "react";
import { ArtifactTreeBranch, type ArtifactTreeCommand } from "./ArtifactTreeBranch";

export type CategorizedArtifactTreeItem = { id: string; categories?: unknown; searchValue?: unknown; render: (appearanceKey: string) => ReactNode };
type CategoryNode = { name: string; path: string; items: CategorizedArtifactTreeItem[]; children: Map<string, CategoryNode> };

export function categoryPaths(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.filter((entry): entry is string => typeof entry === "string").map(entry => entry.split("/").map(part => part.trim()).filter(Boolean).join("/")).filter(Boolean))];
}
function title(value: string) { return value.replace(/[-_]+/g, " ").replace(/\b\w/g, letter => letter.toUpperCase()); }
function count(node: CategoryNode): number { return node.items.length + [...node.children.values()].reduce((total, child) => total + count(child), 0); }
function CategoryHeader({ label, itemCount, special }: { label: string; itemCount: number; special?: "all" | "uncategorized" }) { return <div className={`operation-tree-row operation-category-row ${special ? `category-${special}` : ""}`}><span className="operation-kind-badge">CATEGORY</span><span><b>{label}</b><small>Virtual category</small></span><em>{itemCount} items</em></div>; }
function renderCategory(node: CategoryNode, categoryCommand?: ArtifactTreeCommand): ReactNode {
  const children = [...node.children.values()].sort((a, b) => a.name.localeCompare(b.name));
  return <ArtifactTreeBranch key={`category:${node.path}`} branchCommand={categoryCommand} className="operation-tree-group artifact-category-branch" label={title(node.name)} searchValue={{ category: node.path }} header={<CategoryHeader label={title(node.name)} itemCount={count(node)} />}>
    {node.items.map(item => item.render(`category:${node.path}:${item.id}`))}{children.map(child => renderCategory(child, categoryCommand))}
  </ArtifactTreeBranch>;
}

/** Builds virtual category folders without changing filesystem ownership or resource identity. */
export function CategorizedArtifactTree({ items, showCategories = true, categoryCommand }: { items: CategorizedArtifactTreeItem[]; showCategories?: boolean; categoryCommand?: ArtifactTreeCommand }) {
  const roots = useMemo(() => {
    const result = new Map<string, CategoryNode>();
    for (const item of items) for (const path of categoryPaths(item.categories)) {
      let siblings = result; let accumulated = "";
      for (const segment of path.split("/")) {
        accumulated = accumulated ? `${accumulated}/${segment}` : segment;
        let node = siblings.get(segment);
        if (!node) { node = { name: segment, path: accumulated, items: [], children: new Map() }; siblings.set(segment, node); }
        if (accumulated === path) node.items.push(item);
        siblings = node.children;
      }
    }
    return result;
  }, [items]);
  if (!showCategories) return <div className="categorized-artifact-tree category-flat-all">{items.map(item => item.render(`flat:${item.id}`))}</div>;
  const uncategorized = items.filter(item => categoryPaths(item.categories).length === 0);
  return <div className="categorized-artifact-tree">
    <ArtifactTreeBranch label="All" branchCommand={null} searchValue={{ category: "all" }} header={<CategoryHeader label="All" itemCount={items.length} special="all" />}>{items.map(item => item.render(`all:${item.id}`))}</ArtifactTreeBranch>
    <ArtifactTreeBranch label="Uncategorized" branchCommand={null} searchValue={{ category: "uncategorized" }} header={<CategoryHeader label="Uncategorized" itemCount={uncategorized.length} special="uncategorized" />}>{uncategorized.map(item => item.render(`uncategorized:${item.id}`))}</ArtifactTreeBranch>
    {[...roots.values()].sort((a, b) => a.name.localeCompare(b.name)).map(node => renderCategory(node, categoryCommand))}
  </div>;
}

function categoriesWithin(node: ReactNode): string[] {
  if (!isValidElement(node)) return [];
  const props = node.props as { searchValue?: unknown; children?: ReactNode; [key: string]: unknown };
  const search = props.searchValue;
  const candidate = search && typeof search === "object" ? search as { categories?: unknown; document?: { categories?: unknown } } : undefined;
  const direct = categoryPaths(candidate?.document?.categories ?? candidate?.categories);
  const nested = Children.toArray(props.children).flatMap(categoriesWithin);
  return [...new Set([...direct, ...nested])];
}

function topLevelNodes(node: ReactNode): ReactElement[] {
  return Children.toArray(node).flatMap(child => {
    if (!isValidElement(child)) return [];
    const props = child.props as { children?: ReactNode; className?: string };
    if (child.type === Fragment || String(props.className || "").includes("inheritance-tree")) return topLevelNodes(props.children);
    return [child];
  });
}

/** Adapts existing rich tree branches to the shared virtual-category contract. */
export function CategorizedArtifactNodes({ children, showCategories = true, categoryCommand }: { children: ReactNode; showCategories?: boolean; categoryCommand?: ArtifactTreeCommand }) {
  const nodes = topLevelNodes(children);
  const items = nodes.map((node, index) => ({
    id: String(node.key ?? index),
    categories: categoriesWithin(node),
    searchValue: (node.props as { searchValue?: unknown }).searchValue,
    render: (appearanceKey: string) => <Fragment key={appearanceKey}>{node}</Fragment>,
  }));
  return <CategorizedArtifactTree items={items} showCategories={showCategories} categoryCommand={categoryCommand} />;
}
