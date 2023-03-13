import { createSlice } from '@reduxjs/toolkit';

const filesSlice = createSlice({
  name: 'files',
  initialState: {
    genomeFile: { file: null, preprocessed: false },
    mutationFile: { file: null, preprocessed: false },
    nucleosomeMap: { file: null, preprocessed: false }
  },
  reducers: {
    setGenomeFile: (state, action) => {
      state.genomeFile.file = action.payload;
      state.genomeFile.preprocessed = false;
    },
    setMutationFile: (state, action) => {
      state.mutationFile.file = action.payload;
      state.mutationFile.preprocessed = false;
    },
    setNucleosomeMap: (state, action) => {
      state.nucleosomeMap.file = action.payload;
      state.nucleosomeMap.preprocessed = false;
    },
    setPreprocessed: (state, action) => {
      const { fileType, value } = action.payload;
      state[fileType].preprocessed = value;
    }
  },
});

export const { setGenomeFile, setMutationFile, setNucleosomeMap, setPreprocessed } = filesSlice.actions;

export default filesSlice.reducer;