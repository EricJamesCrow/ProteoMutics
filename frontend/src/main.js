const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { dialog } = require('electron');

if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow;
let splashWindow; // Added splashWindow variable

const createSplashWindow = () => { // Added createSplashWindow function
  splashWindow = new BrowserWindow({
    width: 350,
    height: 400,
    frame: false,
    resizable: false,
  });

  splashWindow.loadFile(path.join(__dirname, '../../src/splash.html'));
};

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 810,
    minWidth: 1265,
    minHeight: 640,
    frame: false,
    autoHideMenuBar: true,
    show: false, // Added show: false to hide the main window initially
    webPreferences: {
      preload: path.resolve(__dirname, '../../src/preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
  });

  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  mainWindow.webContents.openDevTools();

  mainWindow.once('ready-to-show', () => { // Added event listener to close splash and show main window
    splashWindow.close();
    mainWindow.show();
  });
};

app.on('ready', () => {
  createSplashWindow(); // Added createSplashWindow call
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.handle('minimize-window', () => {
  mainWindow.minimize();
});

ipcMain.handle('close-window', () => {
  mainWindow.close();
});

ipcMain.handle('maximize-window', () => {
  if (mainWindow.isMaximized()) {
    mainWindow.restore();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.handle('show-file-dialog', async (event, allowedFileTypes) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      {
        name: 'Allowed Files',
        extensions: allowedFileTypes,
      },
    ],
  });
  return result.filePaths[0];
});