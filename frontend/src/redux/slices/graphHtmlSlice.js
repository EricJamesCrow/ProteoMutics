import { createSlice } from '@reduxjs/toolkit';

const graphHtmlSlice = createSlice({
  name: 'graphHtml',
  initialState: {
    graph: null,
    loading: false,
  },
  reducers: {
    setGraphHtml: (state, action) => {
        state.graph = action.payload;
    },
    setGraphHtmlLoading: (state, action) => {
        state.loading = action.payload;
    },
  },
});

export const { setGraphHtml, setGraphHtmlLoading } = graphHtmlSlice.actions;

export default graphHtmlSlice.reducer;