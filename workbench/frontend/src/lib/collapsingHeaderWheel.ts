import { useCallback, useRef } from "react";

/**
 * Collapsing-header wheel contract for hierarchy pages (Tree+UAE and kin).
 *
 * The page root is a scroller that only overflows by its header block
 * (breadcrumb + heading + inspector strip). Wheel-down anywhere over the page
 * scrolls that header out of view FIRST; only then does the pane under the
 * cursor take the wheel. When the cursor sits over non-scrollable chrome the
 * hierarchy tree is scrolled instead, so page-wheeling always works. Wheel-up
 * returns the header once the hovered inner scroller is back at its top.
 *
 * Returns a callback ref: attach it to the page root section. Attaching via
 * callback means conditional/loading renders still get wired the moment the
 * real section mounts.
 */
export function useCollapsingHeaderWheel(
  fallbackScrollerSelector = ".artifact-navigator-content",
) {
  const cleanupRef = useRef<(() => void) | null>(null);
  return useCallback((node: HTMLElement | null) => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    if (!node) return;
    const onWheel = (event: WheelEvent) => {
      const max = node.scrollHeight - node.clientHeight;
      if (max <= 0 || event.ctrlKey) return;
      const innerScroller = () => {
        let el = event.target as HTMLElement | null;
        while (el && el !== node) {
          if (el.scrollHeight > el.clientHeight + 1) {
            const oy = getComputedStyle(el).overflowY;
            if (oy === "auto" || oy === "scroll") return el;
          }
          el = el.parentElement;
        }
        return null;
      };
      const fallback = () => node.querySelector(fallbackScrollerSelector) as HTMLElement | null;
      if (event.deltaY > 0 && node.scrollTop < max - 1) {
        node.scrollTop = Math.min(max, node.scrollTop + event.deltaY);
        event.preventDefault();
      } else if (event.deltaY > 0) {
        if (!innerScroller()) {
          const tree = fallback();
          if (tree && tree.scrollTop < tree.scrollHeight - tree.clientHeight - 1) {
            tree.scrollTop += event.deltaY;
            event.preventDefault();
          }
        }
      } else if (event.deltaY < 0 && node.scrollTop > 0) {
        const inner = innerScroller();
        if (!inner || inner.scrollTop <= 0) {
          node.scrollTop = Math.max(0, node.scrollTop + event.deltaY);
          event.preventDefault();
        }
      } else if (event.deltaY < 0) {
        if (!innerScroller()) {
          const tree = fallback();
          if (tree && tree.scrollTop > 0) {
            tree.scrollTop = Math.max(0, tree.scrollTop + event.deltaY);
            event.preventDefault();
          }
        }
      }
    };
    node.addEventListener("wheel", onWheel, { passive: false });
    cleanupRef.current = () => node.removeEventListener("wheel", onWheel);
  }, [fallbackScrollerSelector]);
}
