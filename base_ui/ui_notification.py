from PyQt5 import QtCore, QtGui, QtWidgets
import base_ui.res

class Ui_Notification(object):
    def setupUi(self, Notification):
        Notification.setObjectName("Notification")
        Notification.resize(400, 200)
        Notification.setMinimumSize(QtCore.QSize(400, 200))
        Notification.setMaximumSize(QtCore.QSize(400, 200))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/laser-beam.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Notification.setWindowIcon(icon)

        self.gridLayoutWidget = QtWidgets.QWidget(Notification)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 405, 201))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.goToAppButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.goToAppButton.sizePolicy().hasHeightForWidth())
        self.goToAppButton.setSizePolicy(sizePolicy)
        self.goToAppButton.setObjectName("goToAppButton")
        self.gridLayout.addWidget(self.goToAppButton, 1, 1, 1, 1)
        self.newModelButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newModelButton.sizePolicy().hasHeightForWidth())
        self.newModelButton.setSizePolicy(sizePolicy)
        self.newModelButton.setObjectName("newModelButton")
        self.gridLayout.addWidget(self.newModelButton, 1, 2, 1, 1)
        self.returnButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.returnButton.sizePolicy().hasHeightForWidth())
        self.returnButton.setSizePolicy(sizePolicy)
        self.returnButton.setObjectName("returnButton")
        self.gridLayout.addWidget(self.returnButton, 1, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setAutoFormatting(QtWidgets.QTextEdit.AutoAll)
        self.textBrowser.setTabChangesFocus(False)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 5)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 2, 0, 1, 4)

        self.retranslateUi(Notification)
        QtCore.QMetaObject.connectSlotsByName(Notification)

    def retranslateUi(self, Notification):
        _translate = QtCore.QCoreApplication.translate
        Notification.setWindowTitle(_translate("Notification", "Notification"))
        self.goToAppButton.setText(_translate("Notification", "Yes, open the app"))
        self.newModelButton.setText(_translate("Notification", "Create a new model"))
        self.returnButton.setText(_translate("Notification", "Return to current app"))
        self.textBrowser.setHtml(_translate("Notification", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Your model has been successfully saved!</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Would you like to switch to an interactive application based on your model? Or create another model?</span></p></body></html>"))




