import React, { useEffect, useState } from "react";
import { Paper, Box } from "@mui/material";
import { Chat } from "./Chat";
import { Header } from "./Header";
import { ChatInput } from "./ChatInput";
import { useSelector } from "react-redux";

const ChatWindow = () => {
  const widgetId = useSelector((state) => state.widget.widgetId);
  
  const [messages, setMessages] = useState([])

  const addMessage = (message) => {
    setMessages(prev => [...prev, message])
  }

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
        <Chat messages={messages}/>
        <ChatInput onSend={addMessage}/>
      </Box>
    </Paper>
  );
};

export default ChatWindow;
