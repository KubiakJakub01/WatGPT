import React from "react";
import { Paper, Box } from "@mui/material";
import { Chat } from "./Chat";
import { Header } from "./Header";
import { ChatInput } from "./ChatInput";

const ChatWindow = () => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: '350px',
        height: '500px',
        borderRadius: "3%",
        display: "flex",
        flexDirection: "column",
        transition: "all 0.3s",
        overflow: "hidden",
      }}
    >
      <Box>
        <Header />
        <Chat />
        <ChatInput />
      </Box>
    </Paper>
  );
};

export default ChatWindow;
