import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Paper,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:5000");

    ws.current.onmessage = (event) => {
      const newMessage = event.data;
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: newMessage, sender: "server" },
      ]);
    };

    return () => {
      ws.current.close();
    };
  }, []);

  const sendMessage = () => {
    if (message.trim()) {
      ws.current.send(message);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: message, sender: "user" },
      ]);
      setMessage("");
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        backgroundColor: "#f5f5f5",
      }}
    >
      <Box
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          marginBottom: 2,
        }}
      >
        <List>
          {messages.map((msg, index) => (
            <ListItem key={index}>
              <Paper
                sx={{
                  padding: 1,
                  backgroundColor: msg.sender === "user" ? "#e3f2fd" : "#fff",
                  alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                }}
              >
                <ListItemText
                  primary={msg.text}
                  secondary={msg.sender === "user" ? "You" : "Server"}
                />
              </Paper>
            </ListItem>
          ))}
        </List>
      </Box>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          padding: "20px",
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <Button
          variant="contained"
          color="primary"
          endIcon={<SendIcon />}
          onClick={sendMessage}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}

export default App;
