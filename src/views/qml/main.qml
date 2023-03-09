import QtQuick
import QtQuick.Window

Window {
    // Determine the physical size (in millimeters) of the screen using the Screen element
    property real screenPhysicalWidth: Screen.width / Screen.pixelDensity
    property real screenPhysicalHeight: Screen.height / Screen.pixelDensity

    // Adjust the size of the window based on the physical size of the screen
    property real scaleFactor: Math.min(screenPhysicalWidth / 360.0, screenPhysicalHeight / 202.5)
    width: Math.round(1280 * scaleFactor)
    height: Math.round(720 * scaleFactor)
    visible: true
    title: qsTr("Hello World")
}
