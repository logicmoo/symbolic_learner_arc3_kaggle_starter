import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TurndownService from "turndown";
import "../styles/help_tabs.css";

const turndown = new TurndownService({
  bulletListMarker: "-",
  codeBlockStyle: "fenced",
  emDelimiter: "*",
  strongDelimiter: "**",
});

function normalizedMarkdown(html: string): string {
  const markdown = turndown.turndown(html).trimEnd();
  return markdown ? `${markdown}\n` : "";
}

// The shared markdown viewer used for the help/docs files. It applies the same special link
// rewrites everywhere it is used:
//   * `?docs=<filter>` links open the docs browser (via onOpenDocs, else a workbench:open-docs
//     window event);
//   * relative `*.md` links navigate within the viewer (via onNavigateMarkdown, else the same
//     open-docs event);
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

  const rendered = <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      a: ({ node: _node, href = "", ...props }) => {
        const docsSearch = href.startsWith("?docs=");
        const localMarkdown = !/^(https?:|mailto:|#)/i.test(href)
          && href.split("#", 1)[0].toLowerCase().endsWith(".md");
        return <a
          {...props}
          href={href}
          target={editable || docsSearch || localMarkdown ? undefined : "_blank"}
          rel={editable || docsSearch || localMarkdown ? undefined : "noreferrer"}
          onClick={editable
            ? event => event.preventDefault()
            : docsSearch
              ? (event) => {
                event.preventDefault();
                const filter = decodeURIComponent(href.slice(6));
                if (onOpenDocs) onOpenDocs(filter);
                else window.dispatchEvent(new CustomEvent("workbench:open-docs", { detail: filter }));
              }
              : localMarkdown
                ? (event) => {
                  event.preventDefault();
                  if (onNavigateMarkdown) onNavigateMarkdown(href);
                  else window.dispatchEvent(new CustomEvent("workbench:open-docs", { detail: href }));
                }
                : undefined}
        />;
      },
    }}
  >{renderedContent}</ReactMarkdown>;

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
