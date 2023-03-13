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
    interpolateMissingData: { value: 0 },
    mutationFile: { file: null, preprocessed: false },
    nucleosomeMap: { method: null, preprocessed: false }
  },
  reducers: {
    updateDataFormatting: (state, action) => {
      state.dataFormatting = { ...state.dataFormatting, ...action.payload };
    }
  },
});

export const { updateDataFormatting } = graphOptionsSlice.actions;

export default graphOptionsSlice.reducer;