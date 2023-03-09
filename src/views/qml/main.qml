import QtQuick
import QtQuick.Window
import Qt.labs.platform 1.1
import './javascript/App.js' as App

Window {
    // Set the initial size of the window to 1280x720
    property int initialWidth: 1280
    property int intiialHeight: 720

    // Determine the physical size (in millimeters) of the screen using the Screen element
    property real screenPhysicalWidth: Screen.width / Screen.pixelDensity
    property real screenPhysicalHeight: Screen.height / Screen.pixelDensity

    // Determine the DPI of the screen using the Screen element
    property real dpi: Screen.logicalDotsPerInch

    property double scaleFactor: App.determineScaleFactor(Qt.platform.os, Screen.devicePixelRatio)

    // Adjust the size of the window based on the scaling factor
    width: Math.round(initialWidth * scaleFactor)
    height: Math.round(intiialHeight * scaleFactor)
    visible: true
    title: qsTr("Hello World")
}
