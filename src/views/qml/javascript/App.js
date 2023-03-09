const determineScaleFactor = (platform, screen) => {
    if(platform === "windows") {
        if(screen === 1.5) {
            return 1
        } else {
            return 1
        }
    } else if(platform === "linux") {
        if(screen === 1) {
            return 1.39
        }
    } else{
        return 1
    }
}

// Basic UI functionality
const closeWindow = () => {
    if(helpPage.visible == true) {
        displayDropDownMenuPages("help")
    } else if(aboutPage.visible == true) {
        displayDropDownMenuPages("about")
    } else if(settingsPage.visible == true) {
        displayDropDownMenuPages("settings")
    }
    else if(closeMainWindow.visible === false && closeMainWindowOverlay.visible === false && clickOffCloseMainWindow.visible === false) {
        closeMainWindow.visible = true
        closeMainWindowOverlay.visible = true
        clickOffCloseMainWindow.visible = true
        closeWindowYesButton.focus = true
    } else {
        closeMainWindow.visible = false
        closeMainWindowOverlay.visible = false
        clickOffCloseMainWindow.visible = false
        closeWindowYesButton.focus = false
        appContainer.focus = true
    }
}


const resetResizeBorders = () => {
    // Resize visibility
    resizeLeft.visible = true
    resizeRight.visible = true
    resizeBottom.visible = true
    resizeWindow.visible = true
}

const maximizeRestore = () => {
    if(windowStatus == 0){
        mainWindow.showMaximized()
        windowStatus = 1
        windowMargin = 0
        resizeLeft.visible = false
        resizeRight.visible = false
        resizeBottom.visible = false
        resizeWindow.visible = false
        btnMaximizeRestore.btnIconSource = "../resources/images/svg_images/restore_icon.svg"
        bg.radius = 0
        topBar.radius = 0
    }
    else{
        mainWindow.showNormal()
        resetResizeBorders()
        windowStatus = 0
        windowMargin = 10
        btnMaximizeRestore.btnIconSource = "../resources/images/svg_images/maximize_icon.svg"
        bg.radius = 10 * scaleFactor
        topBar.radius = 10 * scaleFactor
    }
}

const ifMaximizedWindowRestore = () => {
    if(windowStatus == 1){
        mainWindow.showNormal()
        windowStatus = 0
        windowMargin = 10
        resetResizeBorders()
        btnMaximizeRestore.btnIconSource = "../resources/images/svg_images/maximize_icon.svg"
    }
}

const restoreMargings = () => {
    windowMargin = 10
    windowStatus = 0
    resetResizeBorders()
    btnMaximizeRestore.btnIconSource = "../resources/images/svg_images/maximize_icon.svg"
}