import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#ff6f3c",
    },
    secondary: {
      main: "#155263",
    },
    message: {
      primary: "#ffc93c",
      secondary: "#e0e0e0"
    },
    text: {
      primary: "#fff", 
      secondary: "#757575", 
    },
  },
});

export default theme;
