import sys
from PyQt5.QtWidgets import QDialog
from base_ui.ui_notification import Ui_Notification
import subprocess


class NotificationDialog(QDialog):
    def __init__(self, file_name, parent=None):
        super(NotificationDialog, self).__init__(parent)
        self.ui = Ui_Notification()
        self.ui.setupUi(self)

        self.ui.goToAppButton.clicked.connect(lambda: self.openOPV(file_name))
        self.ui.newModelButton.clicked.connect(self.openLTC)
        self.ui.returnButton.clicked.connect(self.close)

    def openLTC(self):
        subprocess.Popen([sys.executable, "LTC.py"])
        exit(0)

    def openOPV(self, file_name):
        subprocess.Popen([sys.executable, "OPV.py", file_name])
        exit(0)

