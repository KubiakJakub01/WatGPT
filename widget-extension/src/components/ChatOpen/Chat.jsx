import { Box } from "@mui/material";
import { ChatMessage } from "./ChatMessage";


export const Chat = ({ messages }) => {
  return (
    <Box
      sx={{
        height: "370px",
        overflowY: "auto",
        p: 2,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {messages?.map((msg, idx) => (
        <ChatMessage key={idx} text={msg.text} sender={msg.sender} />
      ))}
    </Box>
  );
};
