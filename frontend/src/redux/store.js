import { configureStore } from '@reduxjs/toolkit';

import filesReducer from './slices/filesSlice';
import graphOptionsReducer from './slices/graphOptionsSlice';
import graphHtmlReducer from './slices/graphHtmlSlice';

export default configureStore({
    reducer: {
        files: filesReducer,
        graphOptions: graphOptionsReducer,
        graphHtml: graphHtmlReducer
    }
})