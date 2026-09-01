export const LIVE_UI_COMMAND_EVENT = "workbench:live-ui-command";

export const LIVE_UI_STYLE_PROPERTIES = [
  "width",
  "height",
  "minWidth",
  "minHeight",
  "maxWidth",
  "maxHeight",
  "display",
  "position",
  "left",
  "right",
  "top",
  "bottom",
  "overflow",
  "overflowX",
  "overflowY",
  "resize",
  "gridTemplateColumns",
  "gridTemplateRows",
  "gap",
  "padding",
  "margin",
  "fontSize",
  "lineHeight",
  "color",
  "background",
  "borderColor",
  "opacity",
] as const;

export type LiveUiStyleProperty = typeof LIVE_UI_STYLE_PROPERTIES[number];

export type LiveUiCommand =
  | {
    kind: "style";
    selector: string;
    styles: Partial<Record<LiveUiStyleProperty, string>>;
    description: string;
  }
  | {
    kind: "class";
    selector: string;
    className: `live-ui-${string}`;
    enabled: boolean;
    description: string;
  }
  | {
    kind: "scroll";
    selector: string;
    description: string;
  };

export function sendLiveUiCommand(command: LiveUiCommand): void {
  window.dispatchEvent(new CustomEvent<LiveUiCommand>(LIVE_UI_COMMAND_EVENT, { detail: command }));
}
