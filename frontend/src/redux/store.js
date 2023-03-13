import { configureStore } from '@reduxjs/toolkit';

import filesReducer from './slices/filesSlice';

export default configureStore({
    reducer: {
        files: filesReducer
    }
})