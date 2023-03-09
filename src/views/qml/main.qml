import QtQuick
import QtQuick.Window

Window {
    // Determine the physical size (in millimeters) of the screen using the Screen element
    property real screenPhysicalWidth: Screen.width / Screen.pixelDensity
    property real screenPhysicalHeight: Screen.height / Screen.pixelDensity

    // Determine the DPI of the screen using the Screen element
    property real dpi: Screen.logicalDotsPerInch

    // Adjust the size of the window based on the physical size of the screen and the DPI of the screen
    property real scaleFactor: Math.min(screenPhysicalWidth / (dpi * 5.5 / 2.54), screenPhysicalHeight / (dpi * 3.1 / 2.54))
    width: Math.round(1280 * scaleFactor)
    height: Math.round(720 * scaleFactor)
    visible: true
    title: qsTr("Hello World")
}
