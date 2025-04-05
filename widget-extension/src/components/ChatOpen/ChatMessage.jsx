import React from "react";
import { Box, Typography, Avatar } from "@mui/material";

export const ChatMessage = ({ text, sender }) => {
  const isUser = sender === "user";

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        mb: 1,
      }}
    >
      {!isUser && <Avatar sx={{ mr: 1, width: 30, height: 30 }}>A</Avatar>}
      <Box
        sx={{
          backgroundColor: isUser ? "message.primary" : "message.secondary",
          color: isUser ? "white" : "black",
          px: 2,
          py: 1,
          borderRadius: 2,
          maxWidth: "60%",
        }}
      >
        <Typography variant="body2">{text}</Typography>
      </Box>
      {isUser && <Avatar sx={{ ml: 1, width: 30, height: 30 }}>U</Avatar>}
    </Box>
  );
};
