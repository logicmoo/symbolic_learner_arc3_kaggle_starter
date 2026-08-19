import { Component, Fragment, useEffect, useMemo, useState, type CSSProperties, type ErrorInfo, type ReactNode, type Ref } from "react";
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
  deferComponentInitialization?: boolean;
  stackIdForColumn?: (column: WorkflowPageColumn) => string;
  renderColumnDivider?: (
    left: WorkflowPageColumn,
    right: WorkflowPageColumn,
    index: number,
  ) => ReactNode;
};

export type WorkflowPageMemberSurface = {
  content: ReactNode;
  itemHeader?: ReactNode;
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

type MemberRenderErrorBoundaryProps = {
  memberId: string;
  componentName: string;
  children: ReactNode;
};

type MemberRenderErrorBoundaryState = {
  error: Error | null;
  stack: string;
};

class MemberRenderErrorBoundary extends Component<MemberRenderErrorBoundaryProps, MemberRenderErrorBoundaryState> {
  constructor(props: MemberRenderErrorBoundaryProps) {
    super(props);
    this.state = { error: null, stack: "" };
  }

  static getDerivedStateFromError(error: Error): MemberRenderErrorBoundaryState {
    return { error, stack: "" };
  }

  componentDidCatch(_error: Error, info: ErrorInfo) {
    this.setState({ stack: info.componentStack || "" });
  }

  render() {
    const { error, stack } = this.state;
    if (!error) return this.props.children;
    return <section className="workflow-page-component-error-detail">
      <div className="validation bad">
        <b>COMPONENT RENDER FAILED</b>
        <span>{error.message || "Unknown component render error"}</span>
      </div>
      <div className="operation-abstract-summary">
        <div><span>COMPONENT</span><code>{this.props.componentName}</code></div>
        <div><span>MEMBER ID</span><code>{this.props.memberId}</code></div>
      </div>
      <pre>{error.stack || stack || error.message}</pre>
    </section>;
  }
}

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
  deferComponentInitialization = false,
  stackIdForColumn,
  renderColumnDivider,
}: Props) {
  const columns = definition.layout?.columns || [];
  const completeLayout = ["left", "center", "right"].every((id) =>
    columns.some((column) => column.id === id),
  );
  const surface = renderers[definition.renderer];
  const [modes, setModes] = useState<Record<string, AccordionDisplayMode>>({});
  const [initAttempts, setInitAttempts] = useState<Record<string, number>>({});
  const [componentOverrides, setComponentOverrides] = useState<Record<string, string>>({});
  const [initializationPassReady, setInitializationPassReady] = useState(!deferComponentInitialization);
  const componentOptions = useMemo(
    () => componentRegistry ? Object.keys(componentRegistry).sort((left, right) => left.localeCompare(right)) : [],
    [componentRegistry],
  );
  const orderedColumns = useMemo(
    () => ["left", "center", "right"].map((id) =>
      columns.find((column) => column.id === id),
    ).filter((column): column is WorkflowPageColumn => Boolean(column)),
    [columns],
  );

  useEffect(() => {
    if (!deferComponentInitialization) {
      setInitializationPassReady(true);
      return;
    }
    setInitializationPassReady(false);
    const handle = window.requestAnimationFrame(() => setInitializationPassReady(true));
    return () => window.cancelAnimationFrame(handle);
  }, [deferComponentInitialization, definition.id, definition.renderer]);

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
                const selectedComponent = componentOverrides[member.id] || member.component;
                const renderer = componentRegistry[selectedComponent];
                const initAttempt = initAttempts[member.id] || 0;
                const shouldInitialize = initializationPassReady || initAttempt > 0 || !deferComponentInitialization;
                let rendered: WorkflowPageMemberSurface;
                if (!shouldInitialize) {
                  rendered = {
                    content: <section className="workflow-page-component-error-detail">
                      <div className="validation good">
                        <b>COMPONENT UNINITIALIZED</b>
                        <span>Deferred initialization mode is active.</span>
                      </div>
                      <div className="operation-abstract-summary">
                        <div><span>COMPONENT</span><code>{selectedComponent}</code></div>
                        <div><span>MEMBER ID</span><code>{member.id}</code></div>
                      </div>
                      <div className="operation-editor-actions">
                        <select
                          aria-label={`Component constructor for ${member.id}`}
                          value={selectedComponent}
                          onChange={(event) => {
                            const next = event.target.value;
                            setComponentOverrides((current) => ({ ...current, [member.id]: next }));
                            setInitAttempts((current) => ({ ...current, [member.id]: 0 }));
                          }}
                        >
                          {[...new Set([selectedComponent, ...componentOptions])].map((name) => <option key={name} value={name}>{name}</option>)}
                        </select>
                        <button
                          type="button"
                          onClick={() => setInitAttempts((current) => ({
                            ...current,
                            [member.id]: (current[member.id] || 0) + 1,
                          }))}
                        >
                          INIT
                        </button>
                      </div>
                      <p>Component is uninitialized. Select INIT to initialize this member immediately, or wait for the next pass.</p>
                    </section>,
                    value: "Uninitialized component",
                    detail: "Waiting for next-pass initialization",
                    baseClass: "english-workflow-panel workflow-page-component-error",
                  };
                } else {
                  try {
                    rendered = renderer
                      ? renderer(member, column)
                      : {
                        content: <section className="workflow-page-component-error-detail">
                          <div className="validation bad">
                            <b>COMPONENT CONSTRUCTOR NOT FOUND</b>
                            <span>{selectedComponent} is not installed for {member.label || member.id}.</span>
                          </div>
                          <div className="operation-abstract-summary">
                            <div><span>COMPONENT</span><code>{selectedComponent}</code></div>
                            <div><span>MEMBER ID</span><code>{member.id}</code></div>
                          </div>
                          <div className="operation-editor-actions">
                            <select
                              aria-label={`Component constructor for ${member.id}`}
                              value={selectedComponent}
                              onChange={(event) => {
                                const next = event.target.value;
                                setComponentOverrides((current) => ({ ...current, [member.id]: next }));
                                setInitAttempts((current) => ({ ...current, [member.id]: 0 }));
                              }}
                            >
                              {[...new Set([selectedComponent, ...componentOptions])].map((name) => <option key={name} value={name}>{name}</option>)}
                            </select>
                            <button
                              type="button"
                              onClick={() => setInitAttempts((current) => ({
                                ...current,
                                [member.id]: (current[member.id] || 0) + 1,
                              }))}
                            >
                              INIT
                            </button>
                          </div>
                          {initAttempt > 0
                            ? <p>Component constructor was not found for {selectedComponent}.</p>
                            : <p>Component is uninitialized. Select INIT to attempt component initialization.</p>}
                        </section>,
                        value: initAttempt > 0 ? "Component constructor not found" : "Uninitialized component",
                        detail: initAttempt > 0 ? `Missing component: ${selectedComponent}` : "Waiting for explicit initialization",
                        baseClass: "english-workflow-panel workflow-page-component-error",
                      };
                  } catch (reason) {
                    const error = reason instanceof Error ? reason : new Error(String(reason));
                    rendered = {
                      content: <section className="workflow-page-component-error-detail">
                        <div className="validation bad">
                          <b>COMPONENT INITIALIZATION FAILED</b>
                          <span>{error.message || "Unknown component initialization error"}</span>
                        </div>
                        <div className="operation-abstract-summary">
                          <div><span>COMPONENT</span><code>{selectedComponent}</code></div>
                          <div><span>MEMBER ID</span><code>{member.id}</code></div>
                        </div>
                        <pre>{error.stack || error.message}</pre>
                      </section>,
                      value: "Component initialization failed",
                      detail: error.message,
                      baseClass: "english-workflow-panel workflow-page-component-error",
                    };
                  }
                }
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
                    itemHeader={rendered.itemHeader}
                    footer={rendered.footer}
                  >
                    <MemberRenderErrorBoundary memberId={member.id} componentName={selectedComponent}>
                      {rendered.content}
                    </MemberRenderErrorBoundary>
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
