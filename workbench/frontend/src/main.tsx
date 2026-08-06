import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./styles/workbench.css";
import "./styles/workspace_backed.css";
import "./styles/llm_models.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
