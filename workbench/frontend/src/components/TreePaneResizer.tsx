import { useCallback, useEffect, useRef } from "react";

const STORAGE_KEY = "arc3.treePaneWidth";

/** Drag handle that resizes the tree column of an `.operation-hierarchy-layout` grid by writing the `--tree-w` CSS variable. Place it as the first child of the workspace (right) pane. */
export function TreePaneResizer({ min = 240, maxFraction = 0.72 }: { min?: number; maxFraction?: number }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const layoutEl = () => ref.current?.closest(".operation-hierarchy-layout") as HTMLElement | null;

  useEffect(() => {
    const layout = layoutEl();
    if (!layout) return;
    const stored = Number(window.localStorage.getItem(STORAGE_KEY) || "");
    if (Number.isFinite(stored) && stored > 0) layout.style.setProperty("--tree-w", `${Math.round(stored)}px`);
  }, []);

  const onPointerDown = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    const layout = layoutEl();
    if (!layout) return;
    event.preventDefault();
    const rect = layout.getBoundingClientRect();
    const prevCursor = document.body.style.cursor;
    const prevSelect = document.body.style.userSelect;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    const move = (moveEvent: PointerEvent) => {
      const max = rect.width * maxFraction;
      const width = Math.max(min, Math.min(max, moveEvent.clientX - rect.left));
      layout.style.setProperty("--tree-w", `${Math.round(width)}px`);
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      document.body.style.cursor = prevCursor;
      document.body.style.userSelect = prevSelect;
      const current = layout.style.getPropertyValue("--tree-w").replace("px", "").trim();
      if (current) window.localStorage.setItem(STORAGE_KEY, current);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  }, [min, maxFraction]);

  const reset = useCallback(() => {
    const layout = layoutEl();
    if (!layout) return;
    layout.style.removeProperty("--tree-w");
    window.localStorage.removeItem(STORAGE_KEY);
  }, []);

  return (
    <div
      ref={ref}
      className="tree-pane-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize tree pane"
      title="Drag to resize · double-click to reset"
      onPointerDown={onPointerDown}
      onDoubleClick={reset}
    />
  );
}
