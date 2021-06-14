from PyQt5.QtWidgets import QDialog
from base_ui.ui_invalid_file_window import Ui_InvalidFileWindow


class InvalidFileWindow(QDialog):
    def __init__(self, parent=None):
        super(InvalidFileWindow, self).__init__(parent)
        self.ui = Ui_InvalidFileWindow()
        self.ui.setupUi(self)