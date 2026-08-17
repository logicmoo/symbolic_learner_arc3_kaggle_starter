import "../styles/three_state_accordion.css";
import { useEffect, useRef, useState, type CSSProperties, type DragEvent, type MouseEvent as ReactMouseEvent, type ReactNode, type Ref } from "react";

export type AccordionDisplayMode = "strip" | "scroll" | "full";

export type AccordionAnchor = "top" | "bottom";

const ACCORDION_MODE_CYCLE: AccordionDisplayMode[] = ["strip", "scroll", "full"];

export function nextAccordionMode(mode: AccordionDisplayMode): AccordionDisplayMode {
  return ACCORDION_MODE_CYCLE[(ACCORDION_MODE_CYCLE.indexOf(mode) + 1) % ACCORDION_MODE_CYCLE.length];
}

const accordionOrders = new Map<string, string[]>();
const accordionOrderListeners = new Set<() => void>();
const accordionModeListeners = new Map<string, Set<(mode: AccordionDisplayMode) => void>>();
const ACCORDION_ORDER_EVENT = "three-state-accordion-order-change";
let activeAccordionDrag: { stackId: string; label: string } | null = null;

function publishAccordionChange(drag: { stackId: string; label: string } | null = activeAccordionDrag) {
  activeAccordionDrag = drag;
  accordionOrderListeners.forEach((listener) => listener());
}

function publishAccordionMode(stackId: string, mode: AccordionDisplayMode) {
  Array.from(accordionModeListeners.get(stackId) || []).forEach((listener) => listener(mode));
}

function storedAccordionOrder(stackId: string) {
  try {
    const stored = JSON.parse(localStorage.getItem(`accordion-order:${stackId}`) || "[]");
    const order = Array.isArray(stored) ? stored.filter((item): item is string => typeof item === "string") : [];
    accordionOrders.set(stackId, order);
    return order;
  } catch {
    accordionOrders.set(stackId, []);
    return [];
  }
}

function publishAccordionOrder(stackId: string, order: string[]) {
  accordionOrders.set(stackId, order);
  localStorage.setItem(`accordion-order:${stackId}`, JSON.stringify(order));
  window.dispatchEvent(new CustomEvent(ACCORDION_ORDER_EVENT, { detail: { stackId } }));
  publishAccordionChange();
  requestAnimationFrame(() => {
    document.querySelectorAll<HTMLElement>(`[data-accordion-stack="${stackId}"][data-accordion-member]`).forEach((member) => {
      const index = order.indexOf(member.dataset.accordionMember || "");
      if (index < 0) return;
      member.style.order = String(index);
      member.style.setProperty("--accordion-member-order", String(index));
    });
  });
}

function useAccordionMemberOrder(stackId: string, label: string, initialIndex?: number, initialPlacementVersion = "v2") {
  const [, refresh] = useState(0);
  useEffect(() => {
    const listener = () => refresh((revision) => revision + 1);
    const storageListener = (event: Event) => {
      if ((event as CustomEvent<{stackId?: string}>).detail?.stackId !== stackId) return;
      accordionOrders.delete(stackId);
      listener();
    };
    accordionOrderListeners.add(listener);
    window.addEventListener(ACCORDION_ORDER_EVENT, storageListener);
    const current = storedAccordionOrder(stackId);
    const firstPlacementKey = `accordion-order-initial-placement:${stackId}:${label}:${initialPlacementVersion}`;
    if (initialIndex !== undefined && !localStorage.getItem(firstPlacementKey)) {
      const withoutMember = current.filter((item) => item !== label);
      withoutMember.splice(Math.max(0, Math.min(initialIndex, withoutMember.length)), 0, label);
      publishAccordionOrder(stackId, withoutMember);
      localStorage.setItem(firstPlacementKey, "true");
    } else if (!current.includes(label)) {
      publishAccordionOrder(stackId, [...current, label]);
    }
    return () => {
      accordionOrderListeners.delete(listener);
      window.removeEventListener(ACCORDION_ORDER_EVENT, storageListener);
    };
  }, [stackId, label, initialIndex, initialPlacementVersion]);
  const order = storedAccordionOrder(stackId);
  return order.indexOf(label) < 0 ? order.length : order.indexOf(label);
}

function moveAccordionMember(stackId: string, source: string, target: string) {
  const current = [...storedAccordionOrder(stackId)];
  const sourceIndex = current.indexOf(source);
  const targetIndex = current.indexOf(target);
  if (sourceIndex < 0 || targetIndex < 0 || sourceIndex === targetIndex) return;
  const nextIndex = sourceIndex + (targetIndex < sourceIndex ? -1 : 1);
  [current[sourceIndex], current[nextIndex]] = [current[nextIndex], current[sourceIndex]];
  publishAccordionOrder(stackId, current);
}

export function ThreeStateAccordionStack({
  id,
  children,
  hostRef,
  className = "",
  controlsLabel,
  freezeControls = false,
}: {
  id: string;
  children?: ReactNode;
  hostRef?: Ref<HTMLDivElement>;
  className?: string;
  controlsLabel?: string;
  freezeControls?: boolean;
}) {
  const [collectiveMode, setCollectiveMode] = useState<AccordionDisplayMode>("scroll");
  const setAllMembers = (mode: AccordionDisplayMode) => {
    setCollectiveMode(mode);
    publishAccordionMode(id, mode);
  };
  return (
    <div ref={hostRef} className={`three-state-accordion-stack ${freezeControls ? "three-state-accordion-stack-frozen-controls" : ""} ${className}`.trim()} data-accordion-stack={id} role="group" aria-label={`${id} accordion stack`}>
      {controlsLabel && <header className="three-state-accordion-member three-state-accordion-stack-controls" data-accordion-stack-control={id}>
        <div className="three-state-accordion-member-strip">
          <button type="button" className="three-state-accordion-member-summary" title={`Cycle every member in ${controlsLabel}`} onClick={() => setAllMembers(nextAccordionMode(collectiveMode))}>
            <span>{controlsLabel}</span>
            <small>Set every member in this stack</small>
          </button>
          <ThreeStateAccordionControls label={controlsLabel} mode={collectiveMode} onChange={setAllMembers} />
        </div>
      </header>}
      {children}
    </div>
  );
}

export function accordionPanelClass(baseClass: string, mode: AccordionDisplayMode, anchor: AccordionAnchor = "top") {
  return `${baseClass} three-state-accordion three-state-accordion-${mode} three-state-accordion-anchor-${anchor}`;
}

export function ThreeStateAccordionMember({
  id,
  stackId,
  memberKey,
  managedOrder,
  label,
  value,
  detail,
  mode,
  onChange,
  baseClass,
  accessories,
  stripContent,
  itemHeader,
  scrollSize = "320px",
  initialIndex,
  initialPlacementVersion,
  children,
  footer,
}: {
  id?: string;
  stackId: string;
  memberKey?: string;
  managedOrder?: number;
  label: string;
  value?: string;
  detail?: string;
  mode: AccordionDisplayMode;
  onChange: (mode: AccordionDisplayMode) => void;
  baseClass: string;
  accessories?: ReactNode;
  stripContent?: (cycleMode: () => void) => ReactNode;
  itemHeader?: ReactNode;
  scrollSize?: string;
  initialIndex?: number;
  initialPlacementVersion?: string;
  children?: ReactNode;
  footer?: ReactNode;
}) {
  const orderKey = memberKey || label;
  const memberOrder = useAccordionMemberOrder(stackId, orderKey, initialIndex, initialPlacementVersion);
  const layoutOrder = managedOrder ?? memberOrder;
  const [dragging, setDragging] = useState(false);
  const suppressClick = useRef(false);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;
  const changeMode = (nextMode: AccordionDisplayMode) => {
    onChange(nextMode);
  };
  useEffect(() => {
    const setFromStack = (nextMode: AccordionDisplayMode) => {
      onChangeRef.current(nextMode);
    };
    const listeners = accordionModeListeners.get(stackId) || new Set<(mode: AccordionDisplayMode) => void>();
    listeners.add(setFromStack);
    accordionModeListeners.set(stackId, listeners);
    return () => {
      listeners.delete(setFromStack);
      if (!listeners.size && accordionModeListeners.get(stackId) === listeners) accordionModeListeners.delete(stackId);
    };
  }, [stackId]);
  const effectiveMode = activeAccordionDrag?.stackId === stackId ? "strip" : mode;
  const beginDrag = (event: DragEvent<HTMLButtonElement>) => {
    if (managedOrder !== undefined) {
      event.preventDefault();
      return;
    }
    setDragging(true);
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("application/x-three-state-accordion", JSON.stringify({ stackId, label: orderKey }));
    setTimeout(() => publishAccordionChange({ stackId, label: orderKey }), 0);
  };
  const beginPointerDrag = (event: ReactMouseEvent<HTMLButtonElement>) => {
    if (event.button !== 0 || managedOrder !== undefined) return;
    const startY = event.clientY;
    let moved = false;
    const move = (mouseEvent: MouseEvent) => {
      if (!moved && Math.abs(mouseEvent.clientY - startY) >= 8) {
        moved = true;
        suppressClick.current = true;
        setDragging(true);
        publishAccordionChange({ stackId, label: orderKey });
      }
      if (moved) mouseEvent.preventDefault();
    };
    const finish = (mouseEvent: MouseEvent) => {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", finish);
      if (moved) {
        let target = document.elementFromPoint(mouseEvent.clientX, mouseEvent.clientY)?.closest<HTMLElement>("[data-accordion-member]");
        if (target?.dataset.accordionStack !== stackId || target.dataset.accordionMember === orderKey) {
          target = Array.from(document.querySelectorAll<HTMLElement>("[data-accordion-member]"))
            .filter((member) => member.dataset.accordionStack === stackId && member.dataset.accordionMember !== orderKey)
            .sort((left, right) => {
              const leftRect = left.getBoundingClientRect();
              const rightRect = right.getBoundingClientRect();
              return Math.abs(leftRect.top + leftRect.height / 2 - mouseEvent.clientY)
                - Math.abs(rightRect.top + rightRect.height / 2 - mouseEvent.clientY);
            })[0];
        }
        if (target?.dataset.accordionStack === stackId && target.dataset.accordionMember) {
          moveAccordionMember(stackId, orderKey, target.dataset.accordionMember);
        }
        setDragging(false);
        publishAccordionChange(null);
        requestAnimationFrame(() => { suppressClick.current = false; });
      }
    };
    document.addEventListener("mousemove", move, { passive: false });
    document.addEventListener("mouseup", finish);
  };
  const acceptDrop = (event: DragEvent<HTMLElement>) => {
    event.preventDefault();
    try {
      const source = JSON.parse(event.dataTransfer.getData("application/x-three-state-accordion"));
      if (source.stackId !== stackId || source.label === label) return;
      moveAccordionMember(stackId, source.label, label);
    } catch {
      // Ignore drags that did not originate from an accordion strip.
    }
  };
  return (
    <section
      id={id}
      className={accordionPanelClass(`${baseClass} three-state-accordion-member`, effectiveMode)}
      data-accordion-stack={stackId}
      data-accordion-member={orderKey}
      style={{ "--accordion-scroll-size": scrollSize, "--accordion-member-order": layoutOrder, order: layoutOrder } as CSSProperties}
      onDragOver={(event) => {
        if (event.dataTransfer.types.includes("application/x-three-state-accordion")) {
          event.preventDefault();
          event.dataTransfer.dropEffect = "move";
        }
      }}
      onDrop={acceptDrop}
    >
      <div className={`three-state-accordion-member-strip ${dragging ? "dragging" : ""}`.trim()}>
        {stripContent
          ? <div className="three-state-accordion-member-custom-summary">{stripContent(() => changeMode(nextAccordionMode(mode)))}</div>
          : <button type="button" className="three-state-accordion-member-summary" draggable={managedOrder === undefined} title={managedOrder === undefined ? `Drag to reorder or click to cycle ${label}` : `Click to cycle ${label}`} onMouseDown={beginPointerDrag} onDragStart={beginDrag} onDragEnd={() => { setDragging(false); publishAccordionChange(null); }} onClick={() => { if (!suppressClick.current) changeMode(nextAccordionMode(mode)); }}>
            <span>{label}</span>
            {value && <b>{value}</b>}
            {detail && <small>{detail}</small>}
          </button>}
        {accessories && <div className="three-state-accordion-strip-accessories">{accessories}</div>}
        <ThreeStateAccordionControls label={label} mode={effectiveMode} onChange={changeMode} />
      </div>
      <header className="three-state-accordion-member-item-header">
        {itemHeader ?? <><b>{value || label}</b>{detail && <small>{detail}</small>}</>}
      </header>
      <div className="three-state-accordion-member-body">{children}</div>
      {footer !== null && <footer className="three-state-accordion-member-footer">
        {footer ?? <><b>{value || label}</b>{detail && <span>{detail}</span>}</>}
      </footer>}
    </section>
  );
}

export function ThreeStateAccordionControls({
  label,
  mode,
  onChange,
}: {
  label: string;
  mode: AccordionDisplayMode;
  onChange: (mode: AccordionDisplayMode) => void;
}) {
  return (
    <div className="panel-frame-controls three-state-accordion-controls" role="group" aria-label={`${label} size`}>
      <button type="button" className={mode === "strip" ? "active" : ""} title={`Collapse ${label} to a thin strip`} aria-label={`Collapse ${label} to a thin strip`} aria-pressed={mode === "strip"} onClick={() => onChange("strip")}>−</button>
      <button type="button" className={mode === "scroll" ? "active" : ""} title={`Show ${label} with a scrolling list`} aria-label={`Show ${label} with a scrolling list`} aria-pressed={mode === "scroll"} onClick={() => onChange("scroll")}>*</button>
      <button type="button" className={mode === "full" ? "active" : ""} title={`Show all ${label} content`} aria-label={`Show all ${label} content`} aria-pressed={mode === "full"} onClick={() => onChange("full")}>+</button>
    </div>
  );
}

export function ThreeStateAccordionStripSummary({
  title,
  value,
  onOpen,
  accessories,
  alwaysVisible = false,
}: {
  title: string;
  value?: string;
  onOpen: () => void;
  accessories?: ReactNode;
  alwaysVisible?: boolean;
}) {
  return (
    <div className={`three-state-accordion-strip-summary ${alwaysVisible ? "always-visible" : ""}`.trim()}>
      <button type="button" className="three-state-accordion-strip-summary-main" onClick={onOpen}>
        <span>{title}</span>
        {value && <b>{value}</b>}
      </button>
      {accessories && <div className="three-state-accordion-strip-accessories">{accessories}</div>}
    </div>
  );
}

export function ThreeStateAccordionHeader({
  title,
  value,
  badge,
  detail,
  actions,
  mode,
  onChange,
  className = "",
}: {
  title: string;
  value?: string;
  badge?: string;
  detail?: string;
  actions?: ReactNode;
  mode: AccordionDisplayMode;
  onChange: (mode: AccordionDisplayMode) => void;
  className?: string;
}) {
  const cycle = () => onChange(nextAccordionMode(mode));

  return (
    <header
      className={`three-state-accordion-header ${className}`.trim()}
      role="button"
      tabIndex={0}
      title={`Double-click to cycle ${title}`}
      onDoubleClick={cycle}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          cycle();
        }
      }}
    >
      <span>{title}</span>
      {value && <b>{value}</b>}
      {detail && <small>{detail}</small>}
      {badge && <em>{badge}</em>}
      {actions && <div className="three-state-accordion-header-actions" onDoubleClick={(event) => event.stopPropagation()}>{actions}</div>}
    </header>
  );
}
