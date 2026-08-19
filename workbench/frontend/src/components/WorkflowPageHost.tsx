import { Fragment, useMemo, useState, type CSSProperties, type ReactNode, type Ref } from "react";
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
  columnsClassName?: string;
  columnsStyle?: CSSProperties;
  columnsRef?: Ref<HTMLDivElement>;
  columnsOverlay?: ReactNode;
  freezeColumnControls?: boolean;
  stackIdForColumn?: (column: WorkflowPageColumn) => string;
  renderColumnDivider?: (
    left: WorkflowPageColumn,
    right: WorkflowPageColumn,
    index: number,
  ) => ReactNode;
};

export type WorkflowPageMemberSurface = {
  content: ReactNode;
  value?: string;
  detail?: string;
  footer?: ReactNode;
  accessories?: ReactNode;
  stripDragData?: Record<string, string>;
  baseClass?: string;
  scrollSize?: string;
  hidden?: boolean;
  mode?: AccordionDisplayMode;
  onModeChange?: (mode: AccordionDisplayMode) => void;
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
  columnsClassName = "",
  columnsStyle,
  columnsRef,
  columnsOverlay,
  freezeColumnControls = false,
  stackIdForColumn,
  renderColumnDivider,
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
      <div
        ref={columnsRef}
        className={`english-workflow-columns ${columnsClassName}`.trim()}
        style={columnsStyle}
      >
        {orderedColumns.map((column, columnIndex) => {
          const stackId = stackIdForColumn?.(column) || `${definition.id}-${column.id}-stack`;
          const nextColumn = orderedColumns[columnIndex + 1];
          return <Fragment key={column.id}>
            <ThreeStateAccordionStack
              id={stackId}
              className={`english-workflow-column workflow-page-${column.role || column.id}`}
              controlsLabel={`${column.label} STACK`}
              freezeControls={freezeColumnControls}
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
                const mode = rendered.mode || modes[member.id] || displayMode(member);
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
                    onChange={(nextMode) => rendered.onModeChange
                      ? rendered.onModeChange(nextMode)
                      : setModes((current) => ({
                        ...current,
                        [member.id]: nextMode,
                      }))}
                    baseClass={rendered.baseClass || "english-workflow-panel"}
                    scrollSize={rendered.scrollSize || "calc(100vh - 250px)"}
                    accessories={rendered.accessories}
                    stripDragData={rendered.stripDragData}
                    footer={rendered.footer}
                  >
                    {rendered.content}
                  </ThreeStateAccordionMember>
                );
              })}
            </ThreeStateAccordionStack>
            {nextColumn && renderColumnDivider?.(column, nextColumn, columnIndex)}
          </Fragment>;
        })}
        {columnsOverlay}
      </div>
      {footer}
    </section>
  );
}
