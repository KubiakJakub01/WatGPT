import React from "react";
import { Box, Typography, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useDispatch } from "react-redux";
import { toggleWidget } from "../../store/widgetSlice";


export const Header = () => {
  const dispatch = useDispatch();

  return (
    <Box
      sx={{
        height: "50px",
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 10px",
        backgroundColor: "primary.main"
      }}
    >
      <Box sx={{
        width: "90%",
        display: "flex",
        alignItems: "center",
        color: "text.primary"
      }}>
        <Typography variant="h6" sx={{ flex: 1, textAlign: "center" }}>Wat GPT</Typography>
        <IconButton
         size='small'
         sx={{ color: "text.primary" }}
         onClick={() => dispatch(toggleWidget())}
         >
            <CloseIcon />
        </IconButton>
      </Box>
    </Box>
  );
};
