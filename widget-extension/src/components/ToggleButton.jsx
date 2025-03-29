import {IconButton} from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import CloseIcon from "@mui/icons-material/Close";


export const ToggleButton = ({ isOpen, toggle }) => {
    return (
      <IconButton
        onClick={toggle}
        sx={{
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'flex-end',
          margin: isOpen ? '' : 'auto',
          width: isOpen ? '40px' : 'auto',
          marginTop: isOpen ? '0' : '5px'
        }}
      >
        {isOpen ? <CloseIcon /> : <ChatBubbleOutlineIcon />}
      </IconButton>
    );
  };