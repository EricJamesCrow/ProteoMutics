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