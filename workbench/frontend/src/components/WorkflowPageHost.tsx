import { useMemo, useState, type ReactNode } from "react";
import {
  ThreeStateAccordionMember,
  ThreeStateAccordionStack,
  type AccordionDisplayMode,
} from "./ThreeStateAccordion";

export type WorkflowPageMemberDefinition = {
  id: string;
  label?: string;
  component: string;
  mode?: string;
  initialDisplayMode?: "strip" | "scroll" | "full";
  options?: Record<string, unknown>;
  resource?: {
    kind: string;
    id: string;
  };
  inputs?: Record<string, string>;
  outputs?: Record<string, string>;
  binding?: string;
  operation?: string;
};

export type WorkflowPageMember = string | WorkflowPageMemberDefinition;

export type WorkflowPageColumn = {
  id: "left" | "center" | "right";
  label: string;
  role?: "data" | "authoring" | "details";
  members: WorkflowPageMember[];
};

export type WorkflowPageDefinition = {
  kind: "workflow_page";
  id: string;
  label: string;
  description?: string;
  glyph?: string;
  menuPlacement?: "first" | "middle" | "last";
  order?: number;
  routeView: string;
  renderer: string;
  layout: {
    kind: "three_column_accordion";
    columns: WorkflowPageColumn[];
  };
};

type Props = {
  definition: WorkflowPageDefinition;
  renderers?: Record<string, ReactNode>;
  componentRegistry?: WorkflowPageComponentRegistry;
  header?: ReactNode;
  footer?: ReactNode;
  pageClassName?: string;
};

export type WorkflowPageMemberSurface = {
  content: ReactNode;
  value?: string;
  detail?: string;
  footer?: ReactNode;
  accessories?: ReactNode;
  baseClass?: string;
  scrollSize?: string;
  hidden?: boolean;
};

export type WorkflowPageComponentRenderer = (
  member: WorkflowPageMemberDefinition,
  column: WorkflowPageColumn,
) => WorkflowPageMemberSurface;

export type WorkflowPageComponentRegistry = Record<
  string,
  WorkflowPageComponentRenderer
>;

const displayMode = (
  member: WorkflowPageMemberDefinition,
): AccordionDisplayMode => member.initialDisplayMode || "scroll";

function memberDefinition(member: WorkflowPageMember): WorkflowPageMemberDefinition {
  return typeof member === "string"
    ? { id: member, label: member, component: member }
    : member;
}

export function WorkflowPageHost({
  definition,
  renderers = {},
  componentRegistry,
  header,
  footer,
  pageClassName = "",
}: Props) {
  const columns = definition.layout?.columns || [];
  const completeLayout = ["left", "center", "right"].every((id) =>
    columns.some((column) => column.id === id),
  );
  const surface = renderers[definition.renderer];
  const [modes, setModes] = useState<Record<string, AccordionDisplayMode>>({});
  const orderedColumns = useMemo(
    () => ["left", "center", "right"].map((id) =>
      columns.find((column) => column.id === id),
    ).filter((column): column is WorkflowPageColumn => Boolean(column)),
    [columns],
  );

  if (definition.layout?.kind !== "three_column_accordion" || !completeLayout)
    return (
      <div className="studio-empty">
        Workflow page {definition.label} must declare left, center, and right
        accordion columns.
      </div>
    );
  if (!componentRegistry && !surface)
    return (
      <div className="studio-empty">
        Workflow page renderer {definition.renderer} is not installed.
      </div>
    );

  if (!componentRegistry)
    return (
      <section
        className="workflow-page-host"
        aria-label={definition.label}
        data-workflow-page={definition.id}
        data-workflow-page-renderer={definition.renderer}
        data-workflow-page-columns={columns.map((column) => column.id).join(" ")}
      >
        {surface}
      </section>
    );

  return (
    <section
      className={`workflow-page-host ${pageClassName}`.trim()}
      aria-label={definition.label}
      data-workflow-page={definition.id}
      data-workflow-page-renderer={definition.renderer}
      data-workflow-page-columns={columns.map((column) => column.id).join(" ")}
    >
      {header}
      <div className="english-workflow-columns">
        {orderedColumns.map((column) => {
          const stackId = `${definition.id}-${column.id}-stack`;
          return (
            <ThreeStateAccordionStack
              key={column.id}
              id={stackId}
              className={`english-workflow-column workflow-page-${column.role || column.id}`}
              controlsLabel={`${column.label} STACK`}
            >
              {column.members.map((rawMember, index) => {
                const member = memberDefinition(rawMember);
                const renderer = componentRegistry[member.component];
                const rendered: WorkflowPageMemberSurface = renderer
                  ? renderer(member, column)
                  : {
                    content: <div className="studio-empty">Component {member.component} is not installed for {member.label || member.id}.</div>,
                    value: "Component unavailable",
                  };
                if (rendered.hidden) return null;
                const mode = modes[member.id] || displayMode(member);
                return (
                  <ThreeStateAccordionMember
                    key={member.id}
                    id={member.id}
                    memberKey={member.id}
                    stackId={stackId}
                    initialIndex={index}
                    initialPlacementVersion={`${definition.id}:v1`}
                    label={(member.label || member.id).toUpperCase()}
                    value={rendered.value}
                    detail={rendered.detail}
                    mode={mode}
                    onChange={(nextMode) => setModes((current) => ({
                      ...current,
                      [member.id]: nextMode,
                    }))}
                    baseClass={rendered.baseClass || "english-workflow-panel"}
                    scrollSize={rendered.scrollSize || "calc(100vh - 250px)"}
                    accessories={rendered.accessories}
                    footer={rendered.footer}
                  >
                    {rendered.content}
                  </ThreeStateAccordionMember>
                );
              })}
            </ThreeStateAccordionStack>
          );
        })}
      </div>
      {footer}
    </section>
  );
}
