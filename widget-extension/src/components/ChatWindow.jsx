import React from "react";
import { Paper, Box, Typography } from "@mui/material";
import { Chat } from "./Chat";
import { ToggleButton } from "./ToggleButton";

const ChatWindow = ({ toggle }) => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: 300,
        height: 400,
        borderRadius: "5%",
        display: "flex",
        flexDirection: "column",
        transition: "all 0.3s",
        overflow: "hidden",
      }}
    >
      <Box sx={{ display: "flex", flexDirection: "row" }}>
        <Box sx={{ flex: 1, marginTop: "8px", marginLeft: "35px" }}>
          <Box sx={{ width: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}>
            <Typography>WatGPT</Typography>
          </Box>
        </Box>
        <ToggleButton isOpen={true} toggle={toggle} />
      </Box>
      <Chat />
    </Paper>
  );
};

export default ChatWindow;
