import { createSlice } from '@reduxjs/toolkit';

const graphOptionsSlice = createSlice({
  name: 'graphOptions',
  initialState: {
    dataFormatting: { contexts: { value: "" }, 
                      countComplements: { enabled: true }, 
                      normalizeToContext: { enabled: true }, 
                      normalizeToMedian: { enabled: true }, 
                      removeOutliers: { 
                                    enabled: true, 
                                    value: ""
                                    }
                    },
    dataSmoothing: { enabled: true,
                     method: 'moving', 
                     moving: { windowSize: "" },
                     savgol: { windowSize: "",  polyOrder: ""},
                     loess: { windowSize: "" },
                     median: { windowSize: "" },
                     gaussian: { sigma: "", mode: "" },
                     exponential: { alpha: "" },
                    },
    interpolateMissingData: { enabled: true, value: "linear" },
    mutationFile: { file: null, preprocessed: false },
    nucleosomeMap: { method: null, preprocessed: false }
  },
  reducers: {
    updateDataFormatting: (state, action) => {
      state.dataFormatting = { ...state.dataFormatting, ...action.payload };
    },
    updateDataSmoothing: (state, action) => {
        state.dataSmoothing = { ...state.dataSmoothing, ...action.payload };
      },
    updateInterpolateMissingData: (state, action) => {
        state.interpolateMissingData = { ...state.interpolateMissingData, ...action.payload };
    }
  },
});

export const { updateDataFormatting, updateDataSmoothing, updateInterpolateMissingData } = graphOptionsSlice.actions;

export default graphOptionsSlice.reducer;