import { useEffect, useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";

type SourceTarget = {
  location: string;
  tagName: string;
  className: string;
  attributes: string[];
  color: string;
  left: number;
  top: number;
  transform: string;
};

function targetColor(element: Element): string {
  if (element.matches("button")) return "#ff4fd8";
  if (element.matches("input")) return "#ffe600";
  if (element.matches("select")) return "#00e5ff";
  if (element.matches("textarea")) return "#ff8500";
  if (element.matches('[contenteditable="true"]')) return "#b36bff";
  if (element.matches('[role="separator"]')) return "#39ff14";
  return "#b36bff";
}

/** The element's own class list as a plain string, ignoring SVG elements
 * whose `className` is an SVGAnimatedString rather than a plain string. */
function elementClassName(element: Element): string {
  return typeof element.className === "string" ? element.className.trim() : "";
}

/** Attribute names a CSS selector or test would plausibly key off of, most
 * useful first. Anything else on the element (long class-free div soup,
 * inline styles, etc.) is not interesting enough to show here. */
const NOTABLE_ATTRIBUTES = [
  "id", "role", "type", "name",
  "aria-pressed", "aria-selected", "aria-expanded", "aria-checked", "aria-disabled",
  "checked", "disabled", "href", "title",
];

function truncate(value: string, max: number): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

/** Up to a handful of `attr="value"` pairs worth showing: known interesting
 * attributes first, then every `data-*` attribute (this app's own selectors
 * and tests lean on those heavily), skipping the debug marker itself. */
function notableAttributes(element: Element): string[] {
  const found: string[] = [];
  for (const name of NOTABLE_ATTRIBUTES) {
    if (!element.hasAttribute(name)) continue;
    const value = element.getAttribute(name) ?? "";
    found.push(value ? `${name}="${truncate(value, 40)}"` : name);
  }
  for (const attr of Array.from(element.attributes)) {
    if (attr.name.startsWith("data-") && attr.name !== "data-tsx-source") {
      found.push(`${attr.name}="${truncate(attr.value, 40)}"`);
    }
  }
  return found;
}

/** What Ctrl+C copies while the popup is showing: source location, a
 * selector-like tag/class summary, and every notable attribute found (the
 * on-screen popup only shows the first two, to stay readable). */
function clipboardText(target: SourceTarget): string {
  const selector = target.className
    ? `${target.tagName}.${target.className.split(/\s+/).join(".")}`
    : `${target.tagName} (no class)`;
  const lines = [target.location, selector, ...target.attributes];
  return lines.join("\n");
}

export function TsxSourceLocationPopup() {
  const [target, setTarget] = useState<SourceTarget | null>(null);
  const [justCopied, setJustCopied] = useState(false);

  useEffect(() => {
    let ctrlHeld = false;
    let lastPointer: PointerEvent | null = null;
    let currentTarget: SourceTarget | null = null;
    let copiedTimer: ReturnType<typeof setTimeout> | undefined;

    const show = (next: SourceTarget | null) => {
      currentTarget = next;
      setTarget(next);
    };

    const targetFor = (event: PointerEvent): SourceTarget | null => {
      const origin = event.target instanceof Element ? event.target : null;
      const element = origin?.closest("[data-tsx-source]");
      const location = element?.getAttribute("data-tsx-source");
      if (!element || !location) return null;
      const flipX = event.clientX > window.innerWidth * 0.65;
      const flipY = event.clientY > window.innerHeight - 56;
      return {
        location,
        tagName: element.tagName.toLowerCase(),
        className: elementClassName(element),
        attributes: notableAttributes(element),
        color: targetColor(element),
        left: event.clientX + (flipX ? -14 : 14),
        top: event.clientY + (flipY ? -14 : 18),
        transform: `${flipX ? "translateX(-100%)" : ""} ${flipY ? "translateY(-100%)" : ""}`.trim(),
      };
    };

    // Only show the popup while Control is held, so it does not follow the
    // pointer constantly -- move to inspect an element, hold Control to read
    // its source location and class name, release to dismiss it.
    const inspect = (event: PointerEvent) => {
      lastPointer = event;
      if (!ctrlHeld) return;
      show(targetFor(event));
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Control") {
        if (ctrlHeld) return;
        ctrlHeld = true;
        if (lastPointer) show(targetFor(lastPointer));
        return;
      }
      // Ctrl+C while the popup is up (Control never released) copies its
      // text instead of whatever the OS/browser would otherwise copy.
      if (event.ctrlKey && (event.key === "c" || event.key === "C") && currentTarget) {
        event.preventDefault();
        void navigator.clipboard.writeText(clipboardText(currentTarget)).then(() => {
          setJustCopied(true);
          clearTimeout(copiedTimer);
          copiedTimer = setTimeout(() => setJustCopied(false), 900);
        });
      }
    };
    const onKeyUp = (event: KeyboardEvent) => {
      if (event.key !== "Control") return;
      ctrlHeld = false;
      show(null);
    };
    const clear = () => {
      ctrlHeld = false;
      show(null);
    };
    document.addEventListener("pointermove", inspect, true);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    window.addEventListener("blur", clear);
    return () => {
      document.removeEventListener("pointermove", inspect, true);
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      window.removeEventListener("blur", clear);
      clearTimeout(copiedTimer);
    };
  }, []);

  if (!target) return null;
  return createPortal(
    <div
      data-tsx-source-popup
      data-tsx-source-popup-copied={justCopied || undefined}
      style={{
        "--tsx-debug-color": target.color,
        left: target.left,
        top: target.top,
        transform: target.transform,
      } as CSSProperties}
    >
      <div data-tsx-source-popup-location>{target.location}</div>
      <div data-tsx-source-popup-class>
        {target.tagName}
        {target.className ? `.${target.className.split(/\s+/).join(".")}` : " (no class)"}
      </div>
      {target.attributes.length > 0 && (
        <div data-tsx-source-popup-attrs>{target.attributes.slice(0, 2).join("  ")}</div>
      )}
      {justCopied && <div data-tsx-source-popup-copied-label>Copied ⌘</div>}
    </div>,
    document.body,
  );
}
