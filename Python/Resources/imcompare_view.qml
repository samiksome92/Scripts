import QtQuick.Controls 2.15
import QtQuick 2.15

Page {
    Rectangle {
        anchors.fill: parent

        color: "#212121"
    }

    Item {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: info.top

        Image {
            anchors.left: parent.left
            anchors.right: parent.horizontalCenter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 2
            anchors.rightMargin: 1
            anchors.topMargin: 2
            anchors.bottomMargin: 2

            source: img_left
            sourceSize.width: 1000
            fillMode: Image.PreserveAspectFit
            horizontalAlignment: Image.AlignRight
            verticalAlignment: Image.AlignBottom

            MouseArea {
                anchors.fill: parent

                onClicked: backend.next("left")
            }
        }

        Image {
            anchors.left: parent.horizontalCenter
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 1
            anchors.rightMargin: 2
            anchors.topMargin: 2
            anchors.bottomMargin: 2

            source: img_right
            sourceSize.width: 1000
            fillMode: Image.PreserveAspectFit
            horizontalAlignment: Image.AlignLeft
            verticalAlignment: Image.AlignBottom

            MouseArea {
                anchors.fill: parent

                onClicked: backend.next("right")
            }
        }
    }

    Item {
        id: info

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 100

        Text {
            id: txtLeft

            anchors.left: parent.left
            anchors.right: txtScore.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            leftPadding: 10
            rightPadding: 5
            topPadding: 10
            bottomPadding: 10

            text: txt_left
            textFormat: Text.StyledText
            color: "#fafafa"
            font.pointSize: 14
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignTop
        }

        Text {
            id: txtScore

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            leftPadding: 5
            rightPadding: 5
            topPadding: 10
            bottomPadding: 10

            text: txt_score
            color: "#fafafa"
            font.pointSize: 20
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignTop
        }

        Text {
            id: txtRight

            anchors.left: txtScore.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            leftPadding: 5
            rightPadding: 10
            topPadding: 10
            bottomPadding: 10

            text: txt_right
            textFormat: Text.StyledText
            color: "#fafafa"
            font.pointSize: 14
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignTop
        }

        MouseArea {
            anchors.fill: parent

            onClicked: backend.next("both")
        }
    }
}
