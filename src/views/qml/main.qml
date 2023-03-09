import QtQuick
import QtQuick.Window

Window {
    // Set the initial size of the window to 1280x720
    property int initialWidth: 1280
    property int intiialHeight: 720

    // Determine the physical size (in millimeters) of the screen using the Screen element
    property real screenPhysicalWidth: Screen.width / Screen.pixelDensity
    property real screenPhysicalHeight: Screen.height / Screen.pixelDensity

    // Determine the DPI of the screen using the Screen element
    property real dpi: Screen.logicalDotsPerInch

    // Calculate the scaling factor to make the window appear as if it has a resolution of 1280x720
    property real scaleFactor: Math.min(screenPhysicalWidth / (dpi * 5.5 / 2.54), screenPhysicalHeight / (dpi * 3.1 / 2.54))

    // Adjust the size of the window based on the scaling factor
    width: Math.round(initialWidth)
    height: Math.round(intiialHeight)
    visible: true
    title: qsTr("Hello World")
}
