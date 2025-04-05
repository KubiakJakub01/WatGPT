import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { setWidgetId, toggleWidget } from "../store/widgetSlice";
import ChatIcon from "./ChatClose/ChatIcon";
import ChatWindow from "./ChatOpen/ChatWindow";

const setCookie = (name, value, days = 3) => {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
};

const getCookie = (name) => {
  const cookies = document.cookie.split("; ");
  const cookie = cookies.find((c) => c.startsWith(name + "="));
  return cookie ? cookie.split("=")[1] : null;
};

const Widget = () => {
  const dispatch = useDispatch();
  const widgetOpen = useSelector((state) => state.widget.widgetOpen);

  useEffect(() => {
    let widgetId = getCookie("widgetId");

    if (!widgetId) {
      widgetId = crypto.randomUUID();
      setCookie("widgetId", widgetId, 3);
    }

    dispatch(setWidgetId(widgetId));
  }, [dispatch]);

  return (
    <div 
      style={{
        position: "fixed",
        bottom: 20,
        right: 20,
      }}
    >
      {!widgetOpen && <ChatIcon toggle={() => dispatch(toggleWidget())} />}
      {widgetOpen && <ChatWindow />}
    </div>
  );
};

export default Widget;
