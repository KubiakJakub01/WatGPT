import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store/store";
import Widget from "./components/Widget";
import theme from "./theme";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";


if (!document.getElementById("chat-widget-root")) {
  const rootElement = document.createElement("div");
  rootElement.id = "chat-widget-root";
  document.body.appendChild(rootElement);

  rootElement.style.position = "fixed";
  rootElement.style.bottom = "20px";
  rootElement.style.right = "20px";
  rootElement.style.zIndex = "1000";

  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Widget />
      </ThemeProvider>
    </Provider>
  );
}
