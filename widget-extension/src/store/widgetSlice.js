import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  widgetOpen: JSON.parse(localStorage.getItem("widgetOpen")) || false,
  widgetId: null
};

const widgetSlice = createSlice({
  name: "widget",
  initialState,
  reducers: {
    toggleWidget: (state) => {
      state.widgetOpen = !state.widgetOpen;
      localStorage.setItem("widgetOpen", JSON.stringify(state.widgetOpen));
    },
    setWidgetId: (state, action) => {
      state.widgetId = action.payload;
    },
  },
});

export const { toggleWidget, setWidgetId } = widgetSlice.actions;
export default widgetSlice.reducer;
