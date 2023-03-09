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
    property int windowMargin: 10
    color: "#00000000"
    title: qsTr("Nucelomutics")
    
    // Remove title bar
    flags: Qt.Window | Qt.FramelessWindowHint

        Rectangle {
        id: appContainer
        color: "#F5F5F5"
        radius: 10 * scaleFactor
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        clip: false
        anchors.rightMargin: windowMargin
        anchors.bottomMargin: windowMargin
        anchors.leftMargin: windowMargin
        anchors.topMargin: windowMargin

        Rectangle {
            id: topBar
            color: "#ACACAC"
            height: 36 * scaleFactor
            radius: 10 * scaleFactor
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.rightMargin: 0
            anchors.leftMargin: 0

            Rectangle {
                id: titleBar
                height: 36 * scaleFactor
                color: "#00000000"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                z: 0
                anchors.rightMargin: 0
                anchors.leftMargin: 5  * scaleFactor
                anchors.topMargin: 0
                
                DragHandler {
                    onActiveChanged: if(active){
                                            mainWindow.startSystemMove()
                                            App.ifMaximizedWindowRestore()
                                        }
                    }

            }
        }
        }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.5}D{i:2}
}
##^##*/
