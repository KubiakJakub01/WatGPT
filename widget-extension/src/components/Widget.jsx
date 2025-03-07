import React, { useState, useEffect } from "react";
import { Paper } from "@mui/material";
import { Chat } from './Chat'
import { ToggleButton } from './ToggleButton'

const Widget = () => {
  const [isOpen, setIsOpen] = useState(() => {
    return JSON.parse(localStorage.getItem("chatWidgetIsOpen")) ?? true;
  });

  useEffect(() => {
    localStorage.setItem("chatWidgetIsOpen", JSON.stringify(isOpen));
  }, [isOpen]);

  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: isOpen ? 300 : 50,
        height: isOpen ? 400 : 50,
        borderRadius: isOpen ? '10%' : "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transition: "all 0.3s ease-in-out",
        overflow: "hidden",
      }}
    >
      <ToggleButton isOpen={isOpen} toggle={() => setIsOpen(!isOpen)} />
      {isOpen && <Chat />}
    </Paper>
  );
};

export default Widget;
