/**
 * A CodeMirror `StreamParser` for SWI-Prolog source, in the same
 * `simpleMode` style as the built-in `@codemirror/legacy-modes` lexers this
 * app already uses for languages with no dedicated `@codemirror/lang-*`
 * package (see scheme, erlang, clojure in ResourceSourceEditor.tsx). This
 * repository's `.pl` files (see `prolog/` and
 * `workbench/plugins/task_harness_pl/`) are SWI-Prolog, not Perl, so this
 * gives them real syntax highlighting instead of falling back to Perl's
 * lexer or plain text.
 */
import { simpleMode } from "@codemirror/legacy-modes/mode/simple-mode";

const PROLOG_DIRECTIVE_PREDICATES =
  "module|use_module|ensure_loaded|dynamic|discontiguous|initialization|" +
  "multifile|table|meta_predicate|set_prolog_flag|op|encoding";

export const prolog = simpleMode({
  start: [
    // Comments
    { regex: /%.*/, token: "comment" },
    { regex: /\/\*/, token: "comment", next: "comment" },
    // Numbers: character code (0'c), radix (0x/0o/0b), float, then integer.
    { regex: /0'(?:\\.|.)/, token: "number" },
    { regex: /0[xX][0-9a-fA-F]+|0[oO][0-7]+|0[bB][01]+/, token: "number" },
    { regex: /\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+|\d+/, token: "number" },
    // Strings, back-quoted code lists, and quoted atoms.
    { regex: /"(?:\\.|[^"\\])*"?/, token: "string" },
    { regex: /`(?:\\.|[^`\\])*`?/, token: "string" },
    { regex: /'(?:\\.|[^'\\])*'?/, token: "atom" },
    // Variables start uppercase or _; everything else lowercase-led is an atom.
    { regex: /[A-Z_][A-Za-z0-9_]*/, token: "variable" },
    // Clause/directive operators before the generic symbolic-operator rule.
    { regex: /:-|-->|\?-/, token: "keyword" },
    { regex: new RegExp(`\\b(?:${PROLOG_DIRECTIVE_PREDICATES})\\b(?=\\s*[(.])`), token: "keyword" },
    { regex: /[a-z][A-Za-z0-9_]*/, token: "atom" },
    { regex: /[+\-*/\\^<>=~:.?@#&]+/, token: "operator" },
    { regex: /[(){}\[\]|,!;]/, token: "bracket" },
  ],
  comment: [
    { regex: /[^*]*\*\//, token: "comment", next: "start" },
    { regex: /[^*]+/, token: "comment" },
    { regex: /\*/, token: "comment" },
  ],
  languageData: {
    commentTokens: { line: "%", block: { open: "/*", close: "*/" } },
  },
});
