import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  widgetOpen: JSON.parse(localStorage.getItem("widgetOpen")) || false,
  messages: [],
};

const widgetSlice = createSlice({
  name: "widget",
  initialState,
  reducers: {
    toggleWidget: (state) => {
      state.widgetOpen = !state.widgetOpen;
      localStorage.setItem("widgetOpen", JSON.stringify(state.widgetOpen));
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
  },
});

export const { toggleWidget, addMessage } = widgetSlice.actions;
export default widgetSlice.reducer;
