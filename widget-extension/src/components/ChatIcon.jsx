import React from "react";
import { Paper } from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";

const ChatIcon = ({ toggle }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: 50,
        height: 50,
        borderRadius: "50%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        cursor: "pointer",
        transition: "all 0.3s",
      }}
      onClick={toggle}
    >
      <ChatBubbleOutlineIcon />
    </Paper>
  );
};

export default ChatIcon;
