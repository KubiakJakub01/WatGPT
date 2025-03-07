import React from "react";
import ReactDOM from "react-dom/client";
import Widget from "./components/Widget";

if (!document.getElementById("chat-widget-root")) {
  const rootElement = document.createElement("div");
  rootElement.id = "chat-widget-root";
  document.body.appendChild(rootElement);

  rootElement.style.position = "fixed";
  rootElement.style.bottom = "20px";
  rootElement.style.right = "20px";
  rootElement.style.zIndex = "1000";

  const root = ReactDOM.createRoot(rootElement);
  root.render(<Widget />);
}
