import { useEffect, useRef, useState } from "react";

/** Renders one fenced ```mermaid code block as a live SVG diagram, injected
 * directly into the DOM (not as an `<img>` -- an `<img>` cannot display an
 * SVG's `<foreignObject>` HTML labels, which mermaid uses by default for
 * multi-line/formatted node text, so it silently fails to render for any
 * diagram using them).
 *
 * mermaid.render() is not safe to call twice, rapidly, for the exact same
 * diagram text: it renders fine once, then throws on a fast repeat call.
 * Something upstream of this component (a parent re-render, a remount from
 * a WYSIWYG contentEditable surface's own reconciliation, whatever it is)
 * can mount this component for the same diagram more than once in a burst,
 * so renders are cached by their exact source text at module scope --
 * mermaid.render() only actually runs once per distinct diagram for the
 * life of the page; every other mount asking for that same text reuses the
 * already-resolved (or already in-flight) result instantly, instead of
 * re-invoking mermaid and hitting that failure.
 */
type MermaidRenderResult = { svg: string; bindFunctions?: (element: Element) => void };
const renderCache = new Map<string, Promise<MermaidRenderResult>>();
let renderCounter = 0;

function renderMermaid(code: string): Promise<MermaidRenderResult> {
  const cached = renderCache.get(code);
  if (cached) return cached;
  const promise = (async () => {
    const { default: mermaid } = await import("mermaid");
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "dark" });
    const id = `mermaid-${(renderCounter += 1)}`;
    return mermaid.render(id, code);
  })();
  renderCache.set(code, promise);
  // A failed render must not stay cached forever -- otherwise one bad
  // attempt (e.g. the double-render race above) would permanently shadow
  // every later, potentially successful, attempt for the same diagram.
  promise.catch(() => renderCache.delete(code));
  return promise;
}

export function MermaidDiagram({ code }: { code: string }) {
  const trimmed = code.trim();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rendering, setRendering] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setRendering(true);
    setError(null);
    renderMermaid(trimmed)
      .then(({ svg, bindFunctions }) => {
        if (cancelled || !containerRef.current) return;
        containerRef.current.innerHTML = svg;
        bindFunctions?.(containerRef.current);
      })
      .catch(reason => {
        if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason));
      })
      .finally(() => {
        if (!cancelled) setRendering(false);
      });
    return () => {
      cancelled = true;
    };
  }, [trimmed]);

  if (error) {
    return (
      <div className="mermaid-diagram mermaid-diagram-error" data-mermaid-source={code} contentEditable={false}>
        <p>Mermaid diagram failed to render: {error}</p>
        <pre><code>{code}</code></pre>
      </div>
    );
  }
  return (
    <div className="mermaid-diagram" data-mermaid-source={code} data-rendering={rendering || undefined} contentEditable={false}>
      <div ref={containerRef} />
    </div>
  );
}
