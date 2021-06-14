from PyQt5 import QtCore, QtGui, QtWidgets
import base_ui.res


class Ui_ObjectWidget(object):
    def setupUi(self, ObjectWidget):
        ObjectWidget.setObjectName("ObjectWidget")
        ObjectWidget.resize(296, 40)
        self.vertical_layout = QtWidgets.QVBoxLayout(ObjectWidget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QtWidgets.QGroupBox(ObjectWidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 50, 290, 40))
        self.groupBox.setObjectName("groupBox")
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontal_layout.addStretch()
        self.icon_radius = QtWidgets.QLabel(self.groupBox)
        self.icon_radius.setGeometry(QtCore.QRect(35, 12, 20, 20))
        self.icon_radius.setText("")
        self.icon_radius.setPixmap(QtGui.QPixmap(":/icon-radius.png"))
        self.icon_radius.setScaledContents(True)
        self.icon_radius.setFixedWidth(20)
        self.icon_radius.setFixedHeight(20)
        self.icon_radius.setObjectName("icon_radius")

        self.horizontal_layout.addWidget(self.icon_radius)

        self.radius_object = QtWidgets.QLineEdit(self.groupBox)
        self.radius_object.setGeometry(QtCore.QRect(66, 12, 70, 20))
        self.radius_object.setFixedWidth(70)
        self.radius_object.setObjectName("radius_object")

        self.horizontal_layout.addWidget(self.radius_object)

        self.icon_axis = QtWidgets.QLabel(self.groupBox)
        self.icon_axis.setGeometry(QtCore.QRect(145, 12, 20, 20))
        self.icon_axis.setText("")
        self.icon_axis.setPixmap(QtGui.QPixmap(":/icon-axis.png"))
        self.icon_axis.setScaledContents(True)
        self.icon_axis.setFixedWidth(20)
        self.icon_axis.setFixedHeight(20)
        self.icon_axis.setObjectName("icon_axis")

        self.horizontal_layout.addWidget(self.icon_axis)

        self.axis_displacement = QtWidgets.QLineEdit(self.groupBox)
        self.axis_displacement.setGeometry(QtCore.QRect(174, 12, 100, 20))
        self.axis_displacement.setFixedWidth(100)
        self.axis_displacement.setObjectName("axis_displacement")

        self.horizontal_layout.addWidget(self.axis_displacement)

        self.vertical_layout.addWidget(self.groupBox)
        self.retranslateUi(ObjectWidget)
        QtCore.QMetaObject.connectSlotsByName(ObjectWidget)

    def retranslateUi(self, ObjectWidget):
        _translate = QtCore.QCoreApplication.translate
        ObjectWidget.setWindowTitle(_translate("ObjectWidget", "ObjectWidget"))
        self.groupBox.setTitle(_translate("ObjectWidget", ""))
        self.radius_object.setPlaceholderText(_translate("ObjectWidget", "Radius (mm)"))
        self.axis_displacement.setPlaceholderText(_translate("ObjectWidget", "Axial displacement"))

