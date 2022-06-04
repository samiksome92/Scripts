import QtQuick.Controls 2.15
import QtQuick 2.15

Page {
    focus: true
    
    Rectangle {
        anchors.fill: parent

        color: "#212121"
    }

    Image {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: info.top
        anchors.leftMargin: 1
        anchors.rightMargin: 1
        anchors.topMargin: 1
        anchors.bottomMargin: 1

        source: img
        fillMode: Image.PreserveAspectFit
        verticalAlignment: Image.AlignBottom
    }

    Text {
        id: info

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        padding: 10

        text: txt
        textFormat: Text.StyledText
        color: "#fafafa"
        font.pointSize: 12
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Keys.onPressed: (event) => {
        if (event.key === Qt.Key_Space)
            backend.switch();
        else if (event.key === Qt.Key_Enter)
            backend.choose();
        else if (event.key === Qt.Key_K)
            backend.both();
        else if (event.key === Qt.Key_N)
            backend.next();
    }
}
