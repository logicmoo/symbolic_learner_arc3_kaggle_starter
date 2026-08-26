import { useEffect, useMemo, useRef, useState, type MouseEvent, type ReactNode } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import TurndownService from "turndown";
import { MermaidDiagram } from "./MermaidDiagram";
import "../styles/help_tabs.css";

// A stable module-level reference: an inline `[remarkGfm]` array literal in
// the component body would otherwise be a brand-new array every render,
// which is enough to make react-markdown treat its whole output as changed.
const REMARK_PLUGINS = [remarkGfm];

const turndown = new TurndownService({
  bulletListMarker: "-",
  codeBlockStyle: "fenced",
  emDelimiter: "*",
  strongDelimiter: "**",
});
// A rendered Mermaid diagram replaces its own DOM subtree with an SVG, but
// keeps the original fenced-block source on data-mermaid-source, so editing
// elsewhere in a WYSIWYG surface round-trips the diagram intact instead of
// losing it (Turndown has no built-in idea what an SVG diagram "was").
turndown.addRule("mermaidDiagram", {
  filter: node => node instanceof HTMLElement && node.hasAttribute("data-mermaid-source"),
  replacement: (_content, node) => {
    const source = (node as HTMLElement).getAttribute("data-mermaid-source") || "";
    return `\n\n\`\`\`mermaid\n${source}\n\`\`\`\n\n`;
  },
});

function normalizedMarkdown(html: string): string {
  const markdown = turndown.turndown(html).trimEnd();
  return markdown ? `${markdown}\n` : "";
}

/** Resolve a relative link in the open document against the `docsFile` URL
 * parameter, preserving that parameter's own path style. With
 * `docsFile=C:\...\task_harness_pl\docs\FOO.md`, a link to `../` resolves to
 * `C:\...\task_harness_pl\README.md` (a directory link opens its README) and
 * `01-architecture.md` resolves to `C:\...\docs\01-architecture.md`. Returns
 * null when there is no docsFile parameter to resolve against. */
function resolveAgainstDocsFile(href: string): string | null {
  const current = new URLSearchParams(window.location.search).get("docsFile");
  if (!current) return null;
  const usesBackslash = current.includes("\\");
  let resolved: URL;
  try {
    resolved = new URL(href, `file:///${current.replaceAll("\\", "/")}`);
  } catch {
    return null;
  }
  if (resolved.protocol !== "file:") return null;
  let path = decodeURIComponent(resolved.pathname);
  if (path.endsWith("/")) path += "README.md";
  path = path.replace(/^\/+/, "");
  return usesBackslash ? path.replaceAll("/", "\\") : path;
}

/** Push a new docsFile into the URL and wake the docs page's own popstate
 * restore listener, which loads the file exactly the way a deep link does. */
function navigateToDocsFile(path: string) {
  const url = new URL(window.location.href);
  url.searchParams.set("docsFile", path);
  window.history.pushState(null, "", `${url.pathname}${url.search}${url.hash}`);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

// The shared markdown viewer used for the help/docs files. It applies the same special link
// rewrites everywhere it is used:
//   * `?docs=<filter>` links open the docs browser (via onOpenDocs, else a workbench:open-docs
//     window event);
//   * relative `*.md` and directory links navigate within the viewer: via onNavigateMarkdown
//     when provided, else resolved against the current docsFile URL parameter (see
//     resolveAgainstDocsFile), else the same open-docs event;
//   * every other link opens in a new tab (target=_blank rel=noreferrer).
export function MarkdownDocument({
  content,
  onOpenDocs,
  onNavigateMarkdown,
  className,
  editable = false,
  onChange,
}: {
  content: string;
  onOpenDocs?: (filter: string) => void;
  onNavigateMarkdown?: (href: string) => void;
  className?: string;
  editable?: boolean;
  onChange?: (content: string) => void;
}) {
  const [renderedContent, setRenderedContent] = useState(content);
  const editorRef = useRef<HTMLDivElement | null>(null);
  const focused = useRef(false);
  const pendingContent = useRef(content);

  useEffect(() => {
    if (!focused.current) {
      pendingContent.current = content;
      setRenderedContent(content);
    }
  }, [content]);

  const emitEditableContent = () => {
    if (!editorRef.current || !onChange) return;
    const next = normalizedMarkdown(editorRef.current.innerHTML);
    pendingContent.current = next;
    onChange(next);
  };

  const applyCommand = (command: string, value?: string) => {
    editorRef.current?.focus();
    document.execCommand(command, false, value);
    window.requestAnimationFrame(emitEditableContent);
  };

  // Memoized so react-markdown sees the same `components` object whenever
  // these callbacks/editable truly have not changed, instead of a brand-new
  // object literal on every parent re-render -- react-markdown otherwise
  // reprocesses and remounts its whole output (any embedded MermaidDiagram
  // included) even when the markdown content itself did not change, which is
  // exactly what was making a diagram flicker while typing elsewhere in a
  // WYSIWYG surface.
  const components = useMemo<Components>(() => ({
    a: ({ node: _node, href = "", ...props }) => {
      const docsSearch = href.startsWith("?docs=");
      const bare = href.split("#", 1)[0].split("?", 1)[0];
      // Relative .md links and relative directory links ("../", "curriculum/",
      // "..") both navigate within the docs viewer; a directory resolves to
      // its README.md (see resolveAgainstDocsFile).
      const localDoc = !/^(https?:|mailto:|#|data:)/i.test(href) && bare !== ""
        && (bare.toLowerCase().endsWith(".md") || bare.endsWith("/") || bare === ".." || bare === ".");
      const openLocalDoc = (event: MouseEvent) => {
        event.preventDefault();
        if (onNavigateMarkdown) {
          onNavigateMarkdown(href);
          return;
        }
        const resolved = resolveAgainstDocsFile(href);
        if (resolved) navigateToDocsFile(resolved);
        else window.dispatchEvent(new CustomEvent("workbench:open-docs", { detail: href }));
      };
      return <a
        {...props}
        href={href}
        target={editable || docsSearch || localDoc ? undefined : "_blank"}
        rel={editable || docsSearch || localDoc ? undefined : "noreferrer"}
        onClick={docsSearch
          ? (event: MouseEvent) => {
            event.preventDefault();
            const filter = decodeURIComponent(href.slice(6));
            if (onOpenDocs) onOpenDocs(filter);
            else window.dispatchEvent(new CustomEvent("workbench:open-docs", { detail: filter }));
          }
          : localDoc
            ? openLocalDoc
            : editable
              ? (event: MouseEvent) => event.preventDefault()
              : undefined}
      />;
    },
    // A fenced ```mermaid block renders as a live diagram instead of a
    // code block, in both read-only and WYSIWYG mode -- the diagram keeps
    // its original source on data-mermaid-source (see the Turndown rule
    // above) so editing round-trips it correctly instead of losing it.
    pre: ({ node: _node, children, ...props }) => {
      const child = Array.isArray(children) ? children[0] : children;
      const codeProps = (child as { props?: { className?: string; children?: ReactNode } } | null)?.props;
      const isMermaid = /(?:^|\s)language-mermaid(?:\s|$)/.test(codeProps?.className || "");
      if (isMermaid) {
        const codeChildren = codeProps?.children;
        const code = Array.isArray(codeChildren) ? codeChildren.join("") : String(codeChildren ?? "");
        return <MermaidDiagram code={code} />;
      }
      return <pre {...props}>{children}</pre>;
    },
  }), [editable, onOpenDocs, onNavigateMarkdown]);

  const rendered = useMemo(
    () => <ReactMarkdown remarkPlugins={REMARK_PLUGINS} components={components}>{renderedContent}</ReactMarkdown>,
    [renderedContent, components],
  );

  if (editable && onChange) {
    return <section className={`markdown-wysiwyg ${className ?? ""}`.trim()}>
      <div className="markdown-wysiwyg-toolbar" aria-label="Markdown formatting">
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("formatBlock", "h2")}>Heading</button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("bold")}><b>Bold</b></button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("italic")}><i>Italic</i></button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("insertUnorderedList")}>Bullets</button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("insertOrderedList")}>Numbers</button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => {
          const href = window.prompt("Link URL");
          if (href) applyCommand("createLink", href);
        }}>Link</button>
        <button type="button" onMouseDown={event => event.preventDefault()} onClick={() => applyCommand("formatBlock", "pre")}>Code</button>
      </div>
      <div
        ref={editorRef}
        className="relationship-markdown markdown-body markdown-wysiwyg-surface"
        contentEditable
        suppressContentEditableWarning
        role="textbox"
        aria-multiline="true"
        aria-label="WYSIWYG Markdown editor"
        onFocus={() => { focused.current = true; }}
        onInput={emitEditableContent}
        onBlur={() => {
          focused.current = false;
          emitEditableContent();
          setRenderedContent(pendingContent.current);
        }}
      >{rendered}</div>
    </section>;
  }

  return (
    <article className={`relationship-markdown markdown-body ${className ?? ""}`.trim()}>
      {rendered}
    </article>
  );
}
