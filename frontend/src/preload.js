const { ipcRenderer, contextBridge } = require("electron");
// const { platform } = require("os");
// can be accessed through window.app

contextBridge.exposeInMainWorld("myApp", {
    minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
    closeWindow: () => ipcRenderer.invoke('close-window'),
    maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
    showFileDialog: (allowedFileTypes) => ipcRenderer.invoke('show-file-dialog', allowedFileTypes),
    // platform: platform(), // create a property oj the app object for
    // platform
});