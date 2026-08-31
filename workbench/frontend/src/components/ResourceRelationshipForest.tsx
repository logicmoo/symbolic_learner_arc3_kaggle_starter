import type { ReactNode } from "react";
import { ArtifactTreeBranch } from "./ArtifactTreeBranch";
import { relationshipIds } from "./resourceRelationships";
import type { TreeRelationshipMode } from "./useArtifactTreeFilter";

export type RelationshipTreeResource = {
  id: string;
  implements?: unknown;
  inheritsFrom?: unknown;
  dependsOn?: unknown;
};

export type RelationshipTreeRecord<T extends RelationshipTreeResource> = {
  path: string;
  source?: string;
  workspaceId?: string;
  document?: T;
};

type RenderNodeArgs<T extends RelationshipTreeResource> = {
  record: RelationshipTreeRecord<T>;
  depth: number;
  childCount: number;
  relationshipMode: TreeRelationshipMode;
};

export function relationshipParentIds(
  resource: RelationshipTreeResource,
  relationshipMode: TreeRelationshipMode,
): string[] {
  return relationshipIds(
    relationshipMode === "implementation"
      ? resource.implements
      : relationshipMode === "inheritance"
        ? resource.inheritsFrom
        : resource.dependsOn,
  );
}

export function ResourceRelationshipForest<T extends RelationshipTreeResource>({
  records,
  relationshipMode,
  renderNode,
}: {
  records: RelationshipTreeRecord<T>[];
  relationshipMode: TreeRelationshipMode;
  renderNode: (args: RenderNodeArgs<T>) => ReactNode;
}) {
  const populated = records.filter((record): record is RelationshipTreeRecord<T> & { document: T } => Boolean(record.document));
  const ids = new Set(populated.map(record => record.document.id));
  const children = new Map<string, typeof populated>();
  for (const record of populated) {
    for (const parentId of relationshipParentIds(record.document, relationshipMode)) {
      const rows = children.get(parentId) || [];
      rows.push(record);
      children.set(parentId, rows);
    }
  }
  const roots = populated.filter(record => !relationshipParentIds(record.document, relationshipMode).some(id => ids.has(id)));
  const visibleRoots = roots.length ? roots : populated;
  const renderBranch = (record: (typeof populated)[number], trail: string[]): ReactNode => {
    const item = record.document;
    const descendants = (children.get(item.id) || []).filter(child => !trail.includes(child.document.id));
    return (
      <ArtifactTreeBranch
        key={`${relationshipMode}:${record.source || "resource"}:${record.path}:${trail.join(">")}`}
        label={item.id}
        searchValue={item}
        header={renderNode({ record, depth: trail.length, childCount: descendants.length, relationshipMode })}
      >
        {descendants.length ? descendants.map(child => renderBranch(child, [...trail, item.id])) : undefined}
      </ArtifactTreeBranch>
    );
  };
  return <>{visibleRoots.map(record => renderBranch(record, []))}</>;
}
