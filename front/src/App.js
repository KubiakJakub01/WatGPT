import React, { useState } from "react";
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
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (message.trim()) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: message, sender: "user" },
      ]);
      
      try {
        const response = await axios.post("http://localhost:5000/send-message", { message });
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: response.data.response.message || "Response received", sender: "server" },
        ]);
      } catch (error) {
        console.error("Error sending message:", error);
      }
      
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
