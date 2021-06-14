from PyQt5 import QtCore, QtGui, QtWidgets
import json


class Ui_MainWindow(object):
    TEXT_INFO = 'res\\settings\\text_ui.json'
    WIDTH_SCREEN = 800
    HEIGHT_SCREEN = 600

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.text = json.load(open(Ui_MainWindow.TEXT_INFO))

    def setupUi(self, MainWindow):
        # Настройки главного окна
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 640)
        MainWindow.setMinimumSize(QtCore.QSize(1100, 640))
        MainWindow.setMaximumSize(QtCore.QSize(1100, 640))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('res\img\laser-beam.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(24, 24))
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)

        # Основной виджет, в который вкладываются все остальные
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.central_widget.sizePolicy().hasHeightForWidth())
        self.central_widget.setSizePolicy(sizePolicy)
        self.central_widget.setObjectName("central_widget")

        # Виджет сеточного отображения
        self.grid_layout_widget = QtWidgets.QWidget(self.central_widget)
        self.grid_layout_widget.setGeometry(QtCore.QRect(0, 0, 1741, 699))
        self.grid_layout_widget.setObjectName("grid_layout_widget")
        self.grid_layout = QtWidgets.QGridLayout(self.grid_layout_widget)
        self.grid_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setObjectName("grid_layout")

        # Настройки имени окна
        self.name_window = QtWidgets.QTextBrowser(self.grid_layout_widget)
        self.name_window.setMinimumSize(QtCore.QSize(800, 40))
        self.name_window.setMaximumSize(QtCore.QSize(800, 40))
        self.name_window.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.name_window.setObjectName("name_window")
        self.grid_layout.addWidget(self.name_window, 1, 0, 1, 1)

        # Добавление окна виджета OpenGL
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.grid_layout_widget)
        self.openGLWidget.setMinimumSize(QtCore.QSize(Ui_MainWindow.WIDTH_SCREEN, Ui_MainWindow.HEIGHT_SCREEN))
        self.openGLWidget.setMaximumSize(QtCore.QSize(Ui_MainWindow.WIDTH_SCREEN, Ui_MainWindow.HEIGHT_SCREEN))
        self.openGLWidget.setObjectName("openGLWidget")

        self.grid_layout.addWidget(self.openGLWidget, 2, 0, 1, 1)

        # tab_widget используется для переключения между меню (добавление точек, проверка результата и т.д.)
        self.tab_widget = QtWidgets.QTabWidget(self.grid_layout_widget)
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tab_widget.setObjectName("tab_widget")

        # Главная панель tab_widget
        self.main_tab = QtWidgets.QWidget()
        self.main_tab.setObjectName("main_tab")

        # Кнопка изменения точек
        self.set_points_button = QtWidgets.QPushButton(self.main_tab)
        self.set_points_button.setGeometry(QtCore.QRect(40, 230, 100, 50))
        self.set_points_button.setObjectName("set_points_button")

        # Кнопка изменения вида
        self.change_view_button = QtWidgets.QPushButton(self.main_tab)
        self.change_view_button.setGeometry(QtCore.QRect(150, 230, 100, 50))
        self.change_view_button.setObjectName("change_view_button")

        # Кнопка проверки результата
        self.check_result_button = QtWidgets.QPushButton(self.main_tab)
        self.check_result_button.setGeometry(QtCore.QRect(30, 555, 235, 30))
        self.check_result_button.setObjectName("check_result_button")

        # Кнопка загрузки готовой модели
        self.load_model_button = QtWidgets.QPushButton(self.main_tab)
        self.load_model_button.setGeometry(QtCore.QRect(30, 590, 235, 30))
        self.load_model_button.setObjectName("load_model_button")

        self.click_instruction = QtWidgets.QTextBrowser(self.main_tab)
        self.click_instruction.setGeometry(QtCore.QRect(2, 50, 294, 170))
        self.click_instruction.setObjectName("click_instruction")

        # Меню изменения точек
        self.tab_widget.addTab(self.main_tab, "")
        self.add_tab = QtWidgets.QWidget()
        self.add_tab.setObjectName("add_tab")

        # Поле информации об ожидаемых данных угла на вход
        self.angle_text_box = QtWidgets.QTextBrowser(self.add_tab)
        self.angle_text_box.setGeometry(QtCore.QRect(2, 50, 294, 50))

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.angle_text_box.sizePolicy().hasHeightForWidth())

        self.angle_text_box.setSizePolicy(sizePolicy)
        self.angle_text_box.setObjectName("angle_text_box")

        # Поле для ввода информации об угле
        self.angle_input = QtWidgets.QLineEdit(self.add_tab)
        self.angle_input.setGeometry(QtCore.QRect(2, 100, 294, 30))
        self.angle_input.setObjectName("angle_input")

        # Поле информации об ожидаемых данных расстояния на вход
        self.distance_text_box = QtWidgets.QTextBrowser(self.add_tab)
        self.distance_text_box.setGeometry(QtCore.QRect(2, 130, 294, 50))

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.distance_text_box.sizePolicy().hasHeightForWidth())

        self.distance_text_box.setSizePolicy(sizePolicy)
        self.distance_text_box.setObjectName("distance_text_box")

        # Поле для ввода информации о расстоянии
        self.distance_input = QtWidgets.QLineEdit(self.add_tab)
        self.distance_input.setGeometry(QtCore.QRect(2, 180, 294, 30))
        self.distance_input.setObjectName("distance_input")

        # Кнопка добавления точки
        self.add_button_in_add_tab = QtWidgets.QPushButton(self.add_tab)
        self.add_button_in_add_tab.setGeometry(QtCore.QRect(40, 230, 100, 50))
        self.add_button_in_add_tab.setObjectName("add_button_in_add_tab")

        # Кнопка удаления последней точки
        self.delete_button_in_add_tab = QtWidgets.QPushButton(self.add_tab)
        self.delete_button_in_add_tab.setGeometry(QtCore.QRect(150, 230, 100, 50))
        self.delete_button_in_add_tab.setObjectName("delete_button_in_add_tab")

        # Кнопка возвращения в основное меню
        self.back_button_from_add_tab = QtWidgets.QPushButton(self.add_tab)
        self.back_button_from_add_tab.setGeometry(QtCore.QRect(30, 555, 235, 30))
        self.back_button_from_add_tab.setObjectName("back_button_from_add_tab")

        self.tab_widget.addTab(self.add_tab, "")

        # Меню разрешения неопределённостей
        self.check_tab = QtWidgets.QWidget()
        self.check_tab.setObjectName("check_tab")

        # Текстовое поле с инструкцией о дальнейших действиях
        self.text_info_in_check_tab = QtWidgets.QTextBrowser(self.check_tab)
        self.text_info_in_check_tab.setGeometry(QtCore.QRect(0, 100, 300, 100))
        self.text_info_in_check_tab.setObjectName("text_info_in_check_tab")

        # Кнопка добавления вертикальной линии
        self.add_vert_line_button_in_check_tab = QtWidgets.QPushButton(self.check_tab)
        self.add_vert_line_button_in_check_tab.setGeometry(QtCore.QRect(40, 230, 100, 50))
        self.add_vert_line_button_in_check_tab.setObjectName("add_vert_line_button_in_check_tab")

        # Кнопка добавления горизотальной линии
        self.add_hor_line_button_in_check_tab = QtWidgets.QPushButton(self.check_tab)
        self.add_hor_line_button_in_check_tab.setGeometry(QtCore.QRect(150, 230, 100, 50))
        self.add_hor_line_button_in_check_tab.setObjectName("add_hor_line_button_in_check_tab")

        # Кнопка удаления последней добавленной линии
        self.delete_last_line_button_in_check_tab = QtWidgets.QPushButton(self.check_tab)
        self.delete_last_line_button_in_check_tab.setGeometry(QtCore.QRect(40, 285, 210, 30))
        self.delete_last_line_button_in_check_tab.setObjectName("delete_last_line_button_in_check_tab")

        # Кнопка подтверждения разрешения неопределённости
        self.complete_button_in_check_tab = QtWidgets.QPushButton(self.check_tab)
        self.complete_button_in_check_tab.setEnabled(True)
        self.complete_button_in_check_tab.setGeometry(QtCore.QRect(30, 555, 235, 30))
        self.complete_button_in_check_tab.setObjectName("complete_button_in_check_tab")

        # Кнопка возвращения в главное меню
        self.back_button_from_check_tab = QtWidgets.QPushButton(self.check_tab)
        self.back_button_from_check_tab.setGeometry(QtCore.QRect(30, 590, 235, 30))
        self.back_button_from_check_tab.setObjectName("back_button_from_check_tab")

        self.tab_widget.addTab(self.check_tab, "")

        # Меню просмотра 3D модели
        self.result_tab = QtWidgets.QWidget()
        self.result_tab.setObjectName("result_tab")

        # Кнопка сохранения модели
        self.save_model_in_result_tab = QtWidgets.QPushButton(self.result_tab)
        self.save_model_in_result_tab.setGeometry(QtCore.QRect(30, 560, 235, 30))
        self.save_model_in_result_tab.setObjectName("save_model_in_result_tab")

        # Кнопка возвращения в главное меню
        self.back_button_from_result_tab = QtWidgets.QPushButton(self.result_tab)
        self.back_button_from_result_tab.setGeometry(QtCore.QRect(30, 595, 235, 30))
        self.back_button_from_result_tab.setObjectName("back_button_from_result_tab")

        # Скролл объектов в меню проверки
        self.scroll_area = QtWidgets.QScrollArea(self.result_tab)
        self.scroll_area.setGeometry(QtCore.QRect(0, 40, 296, 511))
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_area_widget_contents = QtWidgets.QWidget()
        self.scroll_area_widget_contents.setGeometry(QtCore.QRect(0, 0, 296, 500))
        self.scroll_area_widget_contents.setObjectName("scroll_area_widget_contents")

        self.objects_layout = QtWidgets.QVBoxLayout()
        self.objects_layout.addStretch()
        self.objects_layout.setDirection(QtWidgets.QVBoxLayout.TopToBottom)
        self.objects_layout.setObjectName("objects_layout")

        self.hor_layout = QtWidgets.QHBoxLayout(self.scroll_area_widget_contents)
        self.hor_layout.addLayout(self.objects_layout)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)

        # Текстовая информация над списком объектов
        self.objects_text_info_in_result_tab = QtWidgets.QTextBrowser(self.result_tab)
        self.objects_text_info_in_result_tab.setGeometry(QtCore.QRect(0, -2, 296, 40))
        self.objects_text_info_in_result_tab.setPlaceholderText("")
        self.objects_text_info_in_result_tab.setObjectName("objects_text_info_in_result_tab")

        self.tab_widget.addTab(self.result_tab, "")

        self.grid_layout.addWidget(self.tab_widget, 1, 1, 3, 1)
        MainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", self.text['window_title']))
        self.set_points_button.setText(_translate("MainWindow", self.text['set_points_button']))
        self.change_view_button.setText(_translate("MainWindow", self.text['change_view_button']))
        self.check_result_button.setText(_translate("MainWindow", self.text['check_result_button']))
        self.load_model_button.setText(_translate("MainWindow", self.text['load_model_button']))
        self.click_instruction.setHtml(_translate("MainWindow", self.text['click_instruction']))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.main_tab), _translate("MainWindow", "Main"))
        self.angle_text_box.setHtml(_translate("MainWindow", self.text['angle_text_box']))
        self.angle_input.setPlaceholderText(_translate("MainWindow", self.text['angle_input']))
        self.distance_text_box.setHtml(_translate("MainWindow", self.text['distance_text_box']))
        self.distance_input.setPlaceholderText(_translate("MainWindow", self.text['distance_input']))
        self.add_button_in_add_tab.setText(_translate("MainWindow", self.text['add_button_in_add_tab']))
        self.back_button_from_add_tab.setText(_translate("MainWindow", self.text['back_button_from_add_tab']))
        self.delete_button_in_add_tab.setText(_translate("MainWindow", self.text['delete_button_in_add_tab']))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.add_tab), _translate("MainWindow", "Add"))
        self.text_info_in_check_tab.setHtml(_translate("MainWindow", self.text['text_info_in_check_tab']))
        self.add_vert_line_button_in_check_tab.setText(
            _translate("MainWindow", self.text['add_vert_line_button_in_check_tab']))
        self.add_hor_line_button_in_check_tab.setText(
            _translate("MainWindow", self.text['add_hor_line_button_in_check_tab']))
        self.delete_last_line_button_in_check_tab.setText(
            _translate("MainWindow", self.text['delete_last_line_button_in_check_tab']))
        self.complete_button_in_check_tab.setText(_translate("MainWindow", self.text['complete_button_in_check_tab']))
        self.back_button_from_check_tab.setText(_translate("MainWindow", self.text['back_button_from_check_tab']))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.check_tab), _translate("MainWindow", "Page"))

        self.save_model_in_result_tab.setText(_translate("MainWindow", self.text['save_model_in_result_tab']))
        self.back_button_from_result_tab.setText(_translate("MainWindow", self.text['back_button_from_result_tab']))
        self.objects_text_info_in_result_tab.setHtml(
            _translate("MainWindow", self.text['objects_text_info_in_result_tab']))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.result_tab), _translate("MainWindow", "View"))
        self.name_window.setHtml(
            _translate("MainWindow", self.text['name_window_part_1'] + "Top View:" + self.text['name_window_part_2']))