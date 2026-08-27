import {
  useCallback,
  useLayoutEffect,
  useRef,
  type TextareaHTMLAttributes,
} from "react";

const BOUNDARY_SELECTOR = [
  ".super-control-body",
  ".uae-single-body",
  ".operation-editor-scroll",
  ".model-editor-document",
  ".main-stage",
].join(",");

export function AutoGrowingTextarea({
  className = "",
  value,
  ...props
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const ref = useRef<HTMLTextAreaElement | null>(null);
  const resize = useCallback(() => {
    const node = ref.current;
    if (!node) return;
    node.style.height = "auto";
    const minimum = Number.parseFloat(window.getComputedStyle(node).minHeight) || 74;
    const boundary = node.closest(BOUNDARY_SELECTOR) as HTMLElement | null;
    const boundaryBottom = Math.min(
      window.innerHeight,
      boundary?.getBoundingClientRect().bottom ?? window.innerHeight,
    );
    const available = Math.max(minimum, boundaryBottom - node.getBoundingClientRect().top - 12);
    const contentHeight = Math.max(minimum, node.scrollHeight);
    node.style.height = `${Math.ceil(Math.min(contentHeight, available))}px`;
    node.style.overflowY = contentHeight > available ? "auto" : "hidden";
  }, []);

  useLayoutEffect(resize, [resize, value]);
  useLayoutEffect(() => {
    const boundary = ref.current?.closest(BOUNDARY_SELECTOR);
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    if (boundary) observer?.observe(boundary);
    window.addEventListener("resize", resize);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", resize);
    };
  }, [resize]);

  return <textarea
    {...props}
    ref={ref}
    value={value}
    className={[
      "tab-input-editor",
      "tab-input-editor--auto-grow",
      "tab-input-editor--manual-resize",
      className,
    ].filter(Boolean).join(" ")}
  />;
}
