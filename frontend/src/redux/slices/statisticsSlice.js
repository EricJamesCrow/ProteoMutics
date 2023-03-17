import { createSlice } from "@reduxjs/toolkit";

const statisticsSlice = createSlice({
    name: "statistics",
    initialState: {
        periodicity: null,
        signalToNoiseRatio: null,
        confidence: null
    },
    reducers: {
        setPeriodicity: (state, action) => {
            state.periodicity = action.payload;
        },
        setSignalToNoiseRatio: (state, action) => {
            state.signalToNoiseRatio = action.payload;
        },
        setConfidence: (state, action) => {
            state.confidence = action.payload;
        },
    },
});

export const { setPeriodicity, setSignalToNoiseRatio, setConfidence } = statisticsSlice.actions;

export default statisticsSlice.reducer;
