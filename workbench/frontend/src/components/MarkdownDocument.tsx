import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../styles/help_tabs.css";

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
}: {
  content: string;
  onOpenDocs?: (filter: string) => void;
  onNavigateMarkdown?: (href: string) => void;
  className?: string;
}) {
  return (
    <article className={`relationship-markdown markdown-body ${className ?? ""}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ node: _node, href = "", ...props }) => {
            const docsSearch = href.startsWith("?docs=");
            const localMarkdown = !/^(https?:|mailto:|#)/i.test(href)
              && href.split("#", 1)[0].toLowerCase().endsWith(".md");
            return <a
              {...props}
              href={href}
              target={docsSearch || localMarkdown ? undefined : "_blank"}
              rel={docsSearch || localMarkdown ? undefined : "noreferrer"}
              onClick={docsSearch
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
      >{content}</ReactMarkdown>
    </article>
  );
}
