import { configureStore, combineReducers, getDefaultMiddleware } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

import filesReducer from './slices/filesSlice';
import graphOptionsReducer from './slices/graphOptionsSlice';
import graphHtmlReducer from './slices/graphHtmlSlice';
import statisticsReducer from './slices/statisticsSlice';

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['graphOptions'],
};

const rootReducer = combineReducers({
  files: filesReducer,
  graphOptions: graphOptionsReducer,
  graphHtml: graphHtmlReducer,
  statistics: statisticsReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware({
    serializableCheck: {
      ignoredActions: ['persist/PERSIST'],
    },
  }),
});

const persistor = persistStore(store);

export { store, persistor };
