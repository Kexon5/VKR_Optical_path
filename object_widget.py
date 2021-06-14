from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from base_ui.ui_object_widget import Ui_ObjectWidget


class ObjectWidget(QWidget):
    def __init__(self, parent=None):
        super(ObjectWidget, self).__init__(parent)
        self.ui = Ui_ObjectWidget()
        self.ui.setupUi(self)

    def set_type(self, title):
        if "Screen" in title:
            self.ui.groupBox.setTitle(title)
            self.ui.axis_displacement.setHidden(True)
            self.ui.icon_axis.setHidden(True)
            self.ui.radius_object.setFixedWidth(100)
            self.ui.horizontal_layout.addSpacerItem(QtWidgets.QSpacerItem(50, 10, QtWidgets.QSizePolicy.Expanding))
        else:
            self.ui.groupBox.setTitle(title)
