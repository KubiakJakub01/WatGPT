import {IconButton} from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import CloseIcon from "@mui/icons-material/Close";


export const ToggleButton = ({ isOpen, toggle }) => {
    return (
      <IconButton
        onClick={toggle}
        sx={{
          position: "absolute",
          top: 10,
          right: 10,
          backgroundColor: "transparent",
        }}
      >
        {isOpen ? <CloseIcon /> : <ChatBubbleOutlineIcon />}
      </IconButton>
    );
  };