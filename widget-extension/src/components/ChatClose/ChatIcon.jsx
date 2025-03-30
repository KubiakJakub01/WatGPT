import React from "react";
import { Paper } from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import { useDispatch } from "react-redux";
import { toggleWidget } from "../../store/widgetSlice";


const ChatIcon = () => {
  const dispatch = useDispatch();

  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: 60,
        height: 60,
        borderRadius: "50%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "primary.main",
        cursor: "pointer",
      }}
      onClick={() => dispatch(toggleWidget())}
    >
      <ChatBubbleOutlineIcon />
    </Paper>
  );
};

export default ChatIcon;
