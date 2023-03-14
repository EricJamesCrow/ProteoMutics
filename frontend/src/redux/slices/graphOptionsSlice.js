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
    dataSmoothing: { method: "moving-average",
                    },
    interpolateMissingData: { enabled: true, value: "linear" },
    mutationFile: { file: null, preprocessed: false },
    nucleosomeMap: { method: null, preprocessed: false }
  },
  reducers: {
    updateDataFormatting: (state, action) => {
      state.dataFormatting = { ...state.dataFormatting, ...action.payload };
    },
    updateInterpolateMissingData: (state, action) => {
        state.interpolateMissingData = { ...state.interpolateMissingData, ...action.payload };
    }
  },
});

export const { updateDataFormatting, updateInterpolateMissingData } = graphOptionsSlice.actions;

export default graphOptionsSlice.reducer;