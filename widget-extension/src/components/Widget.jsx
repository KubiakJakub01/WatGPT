import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { toggleWidget } from "../store/widgetSlice";
import ChatIcon from "./ChatClose/ChatIcon";
import ChatWindow from "./ChatOpen/ChatWindow";

const Widget = () => {
  const dispatch = useDispatch();
  const widgetOpen = useSelector((state) => state.widget.widgetOpen);

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
