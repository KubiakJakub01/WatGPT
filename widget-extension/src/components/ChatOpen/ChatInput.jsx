import { Box, TextField, InputAdornment, IconButton } from "@mui/material";
import React from "react";
import SendIcon from "@mui/icons-material/Send";


export const ChatInput = () => {
    return (
        <Box sx={{  
            height: '80px',
            backgroundColor: "primary.main",
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            <Box sx={{ 
                width: '90%'
            }}>
                <TextField
                    multiline
                    rows={1}
                    variant="outlined"
                    fullWidth
                    placeholder="Napisz wiadomość..."
                    size='small'
                    sx={{
                        backgroundColor: "text.primary",
                        borderRadius: "5px",
                        color: "black",
                        resize: "none",
                        "& .MuiInputBase-root": {
                        overflow: "hidden",
                        },
                        "& .MuiInputBase-input": {
                            color: "black",
                        },
                        "& .MuiOutlinedInput-root": {
                            "& fieldset": {
                              border: "none",
                            },
                            "&:hover fieldset": {
                              border: "none",
                            },
                            "&.Mui-focused fieldset": {
                              border: "none",
                            },
                          },
                    }}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton size='small' color="secondary.main">
                                    <SendIcon />
                                </IconButton>
                            </InputAdornment>
                        )
                    }}
                />
            </Box>
        </Box>
    )
}