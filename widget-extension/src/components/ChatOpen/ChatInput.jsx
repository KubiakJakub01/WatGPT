import { Box, TextField, InputAdornment, IconButton } from "@mui/material";
import React, { useId, useState } from "react";
import SendIcon from "@mui/icons-material/Send";
import { useSelector } from "react-redux";


export const ChatInput = ({ onSend }) => {
    const widgetId = useSelector((state) => state.widget.widgetId);

    const [inputValue, setInputValue] = useState('');

    const onSendClick = () => {
        const message = {
            widgetId,
            messageId:crypto.randomUUID(), 
            text: inputValue,
            sender: 'user'
        }
        onSend(message)
        setInputValue('')
    }

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
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
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
                                <IconButton size='small' color="secondary.main" onClick={onSendClick}>
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