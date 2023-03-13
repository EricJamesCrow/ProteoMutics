import { configureStore } from '@reduxjs/toolkit';

import filesReducer from './slices/filesSlice';
import graphOptionsReducer from './slices/graphOptionsSlice';

export default configureStore({
    reducer: {
        files: filesReducer,
        graphOptions: graphOptionsReducer
    }
})