import { useEffect, useRef, useState } from "react";
import "../styles/colored_tag_combobox.css";

export type ColoredTag = { text: string; color: string };
export type ColoredTagDescription = {
  label: string;
  groupKey: string;
  groupLabel: string;
  tags: ColoredTag[];
  disabled?: boolean;
};

export function ColoredTagCombobox({
  value,
  ids,
  ariaLabel,
  allowNone,
  noneLabel = "(none/null)",
  describe,
  onChange,
  onOpen,
  disabled,
}: {
  value: string;
  ids: string[];
  ariaLabel: string;
  allowNone?: boolean;
  noneLabel?: string;
  describe: (id: string) => ColoredTagDescription;
  onChange: (value: string) => void;
  onOpen?: () => void;
  disabled?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!open) return;
    const onDoc = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);
  const groups = new Map<string, { label: string; ids: string[] }>();
  for (const id of ids) {
    const description = describe(id);
    const group = groups.get(description.groupKey) ?? { label: description.groupLabel, ids: [] };
    group.ids.push(id);
    groups.set(description.groupKey, group);
  }
  const current = value ? describe(value) : null;
  const chips = (tags: ColoredTag[]) => tags.map((tag) => (
    <span key={tag.text} className="colored-combobox-tag" style={{ color: tag.color, borderColor: tag.color }}>
      {tag.text}
    </span>
  ));
  return (
    <div className="colored-combobox" ref={ref}>
      <button
        type="button"
        className="colored-combobox-button"
        aria-label={ariaLabel}
        aria-haspopup="listbox"
        aria-expanded={open}
        disabled={disabled}
        onClick={() => setOpen((currentOpen) => {
          if (!currentOpen) onOpen?.();
          return !currentOpen;
        })}
      >
        <span className="colored-combobox-current">{current ? current.label : noneLabel}</span>
        {current ? chips(current.tags) : null}
        <span className="colored-combobox-caret">▾</span>
      </button>
      {open && (
        <div className="colored-combobox-menu" role="listbox">
          {allowNone && (
            <button
              type="button"
              role="option"
              aria-selected={!value}
              className={`colored-combobox-option${value ? "" : " is-selected"}`}
              onClick={() => { onChange(""); setOpen(false); }}
            >
              <span className="colored-combobox-option-label">{noneLabel}</span>
            </button>
          )}
          {[...groups.keys()].sort((left, right) => left.localeCompare(right)).map((groupKey) => (
            <div key={groupKey} className="colored-combobox-group">
              <div className="colored-combobox-group-header">{groups.get(groupKey)!.label}</div>
              {groups.get(groupKey)!.ids.map((id) => {
                const description = describe(id);
                return (
                  <button
                    key={id}
                    type="button"
                    role="option"
                    aria-selected={id === value}
                    disabled={description.disabled}
                    className={`colored-combobox-option${id === value ? " is-selected" : ""}`}
                    onClick={() => { onChange(id); setOpen(false); }}
                  >
                    <span className="colored-combobox-option-label">{description.label}</span>
                    {chips(description.tags)}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
