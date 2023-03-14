import { createSlice } from '@reduxjs/toolkit';

const graphHtmlSlice = createSlice({
  name: 'graphHtml',
  initialState: '',
  reducers: {
    setGraphHtml: (state, action) => {
        return action.payload;
    }
  },
});

export const { setGraphHtml } = graphHtmlSlice.actions;

export default graphHtmlSlice.reducer;