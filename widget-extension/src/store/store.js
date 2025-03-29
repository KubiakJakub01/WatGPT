import { configureStore } from "@reduxjs/toolkit";
import widgetReducer from "./widgetSlice"; 

const store = configureStore({
  reducer: {
    widget: widgetReducer, 
  },
});

export default store;
