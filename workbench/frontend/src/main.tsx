import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { startCssHotPoll } from "./dev/css_hot_poll";
import "./styles/workbench.css";
import "./styles/workspace_backed.css";
import "./styles/llm_models.css";
import "./styles/model_inheritance_tree.css";

startCssHotPoll();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
