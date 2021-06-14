import subprocess
import sys

import pyrr

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from darktheme.widget_template import DarkPalette
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from PIL import Image


from base_ui.ui_main_window import Ui_MainWindow
from object_widget import ObjectWidget
from notification_dialog import NotificationDialog
from invalid_file_window import InvalidFileWindow
from camera import CameraControl
from utils import *

TEXTURE_SYMBOLS = 'res\\textures\\Verdana.png'
VERTEX_SHADER = 'res\\shaders\\LTC.vert'
FRAGMENT_SHADER = 'res\\shaders\\LTC.frag'

DRAW_SETTINGS = 'res\\settings\\draw_settings.json'


class MainWindow(QMainWindow):
    class Laser:
        def __init__(self):
            self.points = [[[0.0, 0.0]], [[0.0, 0.0]]]
            self.distance_list = [[], []]
            self.total_3D_points = []
            self.scale = [1E-2, -1E-2, 1E-2]
            self.lines = []

    def __init__(self, window):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(window)
        self.window = window
        # Цвет фона
        self.coef_clear_color = [0.2, 0.3, 0.3]
        # Инициализация переменных, связанных с отрисовкой лазера
        self.laser = MainWindow.Laser()

        # Настройки отрисовки из файла
        self.draw_settings = json.load(open(DRAW_SETTINGS))
        # Загрузка исходников вершинного и фрагментного шейдеров
        self.shader = None
        self.vertex_src = open(VERTEX_SHADER, "rb").read()
        self.fragment_src = open(FRAGMENT_SHADER, "rb").read()

        self.controversial_points = dict()
        self.key_points = []
        self.state_view = 1
        # Текущий индекс функции отрисовки и их общий список
        self.index_paint = 0
        self.list_draw_functions = [self.loadViews, self.loadControversialCase, self.load3DScene]
        # Переменные для отрисовки текстур числовых данных
        self.texture = 0
        self.vertex = [0., 0., 1., 0., 1., 1., 0., 1.]
        self.tex_coord = [0., 0., 1., 0., 1., 1., 0., 1.]

        # Временное сохранение точек модели в np
        self.tmp_np_points = [[], []]
        # Переменная, хранящая значение общей оси видов, в которой требуется разрешить проблему конкурирующих точек
        self.current_key = None
        # Заголовки окон
        self.titles = ["Front View:", "Top View:", "Additional information required:", "3D Model:"]
        # Список виджетов, содержащих информацию о предметах в 3D модели
        self.widgets = []
        # Отображение сфер на 3D модели
        self.t = 0.
        self.sign = 1

        self.setBehavior()

    def setBehavior(self):
        # Задание поведения UI элементов
        # Инициализация OpenGL виджета для отрисовки
        self.ui.openGLWidget.initializeGL()
        self.ui.openGLWidget.paintGL = self.paintGL
        self.ui.openGLWidget.initializeGL = self.initializeGL

        # Кнопки главного меню
        self.ui.set_points_button.clicked.connect(lambda: self.clickTransitionButton(0, 1))
        self.ui.change_view_button.clicked.connect(self.clickChangeView)
        self.ui.check_result_button.clicked.connect(self.clickCheckResult)
        self.ui.load_model_button.clicked.connect(self.clickLoad)

        # Кнопки добавления точки
        self.ui.add_button_in_add_tab.clicked.connect(self.addPoint)
        self.ui.delete_button_in_add_tab.clicked.connect(self.clickDeletePoint)
        self.ui.back_button_from_add_tab.clicked.connect(lambda: self.clickTransitionButton(1, 0))

        # Кнопки меню проверки
        self.ui.complete_button_in_check_tab.setEnabled(False)
        self.ui.complete_button_in_check_tab.clicked.connect(self.clickComplete)
        self.ui.add_vert_line_button_in_check_tab.clicked.connect(lambda: self.clickAddLine(0))
        self.ui.add_hor_line_button_in_check_tab.clicked.connect(lambda: self.clickAddLine(1))
        self.ui.delete_last_line_button_in_check_tab.setEnabled(False)
        self.ui.delete_last_line_button_in_check_tab.clicked.connect(self.clickDelLine)
        self.ui.back_button_from_check_tab.clicked.connect(lambda: self.clickTransitionButton(2, 0))

        # Кнопки меню с 3D моделью
        self.ui.back_button_from_result_tab.clicked.connect(lambda: self.clickTransitionButton(3, 0))
        self.ui.save_model_in_result_tab.setEnabled(False)
        self.ui.save_model_in_result_tab.clicked.connect(self.clickSaveModel)

    def clickSaveModel(self):
        data = dict()
        data["Start"] = {"point": self.laser.total_3D_points[0]}
        for i in range(1, len(self.laser.total_3D_points)):
            if "Mirror" in self.widgets[i - 1].ui.groupBox.title():
                data[self.widgets[i - 1].ui.groupBox.title()] = {"point": self.laser.total_3D_points[i],
                                                                 "radius": float(self.widgets[
                                                                                     i - 1].ui.radius_object.text()) / 1000,
                                                                 "displacement": float(self.widgets[
                                                                                           i - 1].ui.axis_displacement.text()) / 1000}
            else:
                data[self.widgets[i - 1].ui.groupBox.title()] = {"point": self.laser.total_3D_points[i],
                                                                 "radius": float(self.widgets[
                                                                                     i - 1].ui.radius_object.text()) / 1000}

        data["Camera"] = {"cam_pos": list(self.cam.cam[self.cam.current_cam].camera_pos),
                          "cam_front": list(self.cam.cam[self.cam.current_cam].camera_front),
                          "cam_up": list(self.cam.cam[self.cam.current_cam].camera_up),
                          "cam_right": list(self.cam.cam[self.cam.current_cam].camera_right)}

        file_name, filt = QtWidgets.QFileDialog.getSaveFileName(self.window, "Save as", "", "JSON File (*.json)",
                                                                options=QtWidgets.QFileDialog.Options() | QtWidgets.QFileDialog.DontUseNativeDialog)
        if file_name:
            with open(file_name + ".json", "w") as fOut:
                json.dump(data, fOut, indent=2)
            dialog = NotificationDialog(file_name)
            dialog.exec()

    def clickLoad(self):
        file_name, filt = QtWidgets.QFileDialog.getOpenFileName(self.window, "Select Model File", "", "JSON File (*.json)",
                                                          options=QtWidgets.QFileDialog.Options() | QtWidgets.QFileDialog.DontUseNativeDialog)



        if checkFile(file_name):
            subprocess.Popen([sys.executable, "OPV.py", file_name])
            exit(0)
        else:
            fail_window = InvalidFileWindow()
            fail_window.exec()


    def clickComplete(self):
        self.controversial_points.pop(self.current_key)
        for i in range(len(self.laser.total_3D_points)):
            if self.laser.total_3D_points[i] is None:
                self.laser.total_3D_points.pop(i)
                for j in range(len(self.key_points)):
                    self.laser.total_3D_points.insert(i + j, [
                        find_nearest(np.array(self.laser.points[0])[:, 0], self.current_key) * self.laser.scale[0],
                        self.key_points[j][1] * self.laser.scale[1], self.key_points[j][0] * self.laser.scale[2]])
                break

        if len(self.controversial_points):
            self.add_vert_line_button_in_check_tab.setEnabled(True)
            self.add_hor_line_button_in_check_tab.setEnabled(True)
            self.laser.lines.clear()
            self.complete_button_in_check_tab.setEnabled(False)
            self.ui.openGLWidget.update()
        else:
            self.clickTransitionButton(2, 3)

    def clickDelLine(self):
        if len(self.laser.lines) > 0:
            mode = self.laser.lines.pop(-1)
            if mode:
                self.ui.add_hor_line_button_in_check_tab.setEnabled(True)
            else:
                self.ui.add_vert_line_button_in_check_tab.setEnabled(True)

            if self.ui.complete_button_in_check_tab.isEnabled():
                self.ui.complete_button_in_check_tab.setEnabled(False)
            self.ui.openGLWidget.update()
        if len(self.laser.lines) == 0:
            self.ui.delete_last_line_button_in_check_tab.setEnabled(False)

    def clickAddLine(self, mode):
        if len(self.laser.lines) <= self.limiter_size[0] + self.limiter_size[1] - 2:
            self.laser.lines.append(mode)

        if self.laser.lines.count(0) == self.limiter_size[0] - 1:
            self.ui.add_vert_line_button_in_check_tab.setEnabled(False)
        if self.laser.lines.count(1) == self.limiter_size[1] - 1:
            self.ui.add_hor_line_button_in_check_tab.setEnabled(False)
        if len(self.laser.lines) == self.limiter_size[0] + self.limiter_size[1] - 2:
            self.ui.complete_button_in_check_tab.setEnabled(True)
        self.ui.delete_last_line_button_in_check_tab.setEnabled(True)
        self.ui.openGLWidget.update()

    def clickTransitionButton(self, curIndex, index):
        self.ui.tab_widget.setCurrentIndex(index)
        if curIndex == 0 and index == 2 or curIndex == 2 and index == 0:
            if index:
                self.changeTitle(self.titles[index])
            else:
                self.changeTitle(self.titles[self.state_view])
            self.index_paint = 1 if index != 0 else 0
            self.ui.openGLWidget.update()
        elif (curIndex == 0 or curIndex == 2) and index == 3 or curIndex == 3 and index == 0:
            if index:
                self.changeTitle(self.titles[index])
                self.index_paint = 2
                self.addObjectsToList()
            else:
                self.changeTitle(self.titles[self.state_view])
                self.index_paint = 0

            self.ui.openGLWidget.update()

    def clickChangeView(self):
        self.state_view = 1 - self.state_view
        self.changeTitle(self.titles[self.state_view])
        self.ui.openGLWidget.update()

    def clickCheckResult(self):
        # Переход к построению 3D модели
        # Алгоритм проходит через уникальные точки на общей оси видов
        # Если нет конкурирующих точек, то алгоритм добавит все точки для 3D модели и перейдёт к отрисовке сцены с ней
        # Если есть, то к отрисовке сцены разрешения
        if not len(self.tmp_np_points[0]):
            self.tmp_np_points[0].append(np.array(self.laser.points[0], dtype=int))
            self.tmp_np_points[1].append(np.array(self.laser.points[1], dtype=int))
            step_top = step_front = 0
            tmp_set = []
            # Надо закинуть в другую переменную, чтобы не упало
            help = [tmp_set.append(i) for i in list(self.tmp_np_points[0][0][:, 0]) if i not in tmp_set]
            for elem in tmp_set:
                tmp_count = [self.counter(list(self.tmp_np_points[0][0][:, 0]), elem),
                             self.counter(list(self.tmp_np_points[1][0][:, 0]), elem)]
                if tmp_count[0] == 1 and tmp_count[1] == 1:
                    self.laser.total_3D_points.append([self.laser.points[1][step_top][0] * self.laser.scale[0],
                                                       self.laser.points[0][step_front][1] * self.laser.scale[1],
                                                       self.laser.points[1][step_top][1] * self.laser.scale[2]])
                elif tmp_count[0] == 1 and tmp_count[1] > 1:
                    self.laser.total_3D_points.append(
                        [self.laser.points[1][step_top][0] * self.laser.scale[0],
                         self.laser.points[0][step_front][1] * self.laser.scale[1],
                         self.laser.points[1][step_top][1] * self.laser.scale[2]])
                    step_top += 1
                    self.laser.total_3D_points.append(
                        [self.laser.points[1][step_top][0] * self.laser.scale[0],
                         self.laser.points[0][step_front][1] * self.laser.scale[1],
                         self.laser.points[1][step_top][1] * self.laser.scale[2]])
                elif tmp_count[0] > 1 and tmp_count[1] == 1:
                    self.laser.total_3D_points.append(
                        [self.laser.points[1][step_top][0] * self.laser.scale[0],
                         self.laser.points[0][step_front][1] * self.laser.scale[1],
                         self.laser.points[1][step_top][1] * self.laser.scale[2]])
                    step_front += 1
                    self.laser.total_3D_points.append(
                        [self.laser.points[1][step_top][0] * self.laser.scale[0],
                         self.laser.points[0][step_front][1] * self.laser.scale[1],
                         self.laser.points[1][step_top][1] * self.laser.scale[2]])
                elif tmp_count[0] > 1 and tmp_count[1] > 1:
                    step_top += tmp_count[1] - 1
                    step_front += tmp_count[0] - 1
                    self.laser.total_3D_points.append(None)
                    self.controversial_points[elem] = tmp_count
                else:
                    print("ERROR")
                    self.tmp_np_points = [[], []]
                    return

                step_top += 1
                step_front += 1
        if len(self.controversial_points):
            self.clickTransitionButton(0, 2)
        else:
            self.clickTransitionButton(0, 3)

    def clickDeletePoint(self):
        if len(self.laser.points[self.state_view]) > 1:
            self.laser.points[self.state_view].pop(-1)
            self.laser.distance_list[self.state_view].pop(-1)
            self.ui.openGLWidget.update()

    def findLookoutPoint(self):
        # Подбор положения и направления просмотра камеры на 3D модель
        self.cam = CameraControl()
        points = np.array(self.laser.total_3D_points)
        prism = np.array([[np.min(points[:, 0]), np.min(points[:, 1]), np.min(points[:, 2])],
                          [np.max(points[:, 0]), np.max(points[:, 1]), np.max(points[:, 2])]])
        avg = np.array(list(map(lambda x: (x[0] + x[1]) / 2, prism.T)))

        list_pos = []
        for x in prism[:, 0]:
            for z in prism[:, 2]:
                v = np.array([x, prism[1][1], z])
                list_pos.append(np.min(list(map(lambda x: distance(x, v), points))))

        ind_cam = np.argmax(list_pos)
        cam_pos = np.array([prism[ind_cam // 2][0], prism[1][1], prism[ind_cam % 2][2]])
        if prism[1][0] - prism[0][0] > prism[1][2] - prism[0][2]:
            cam_front_pos = np.array([avg[0], prism[0][1], prism[1 - (ind_cam % 2)][2]])
        else:
            cam_front_pos = np.array([prism[1 - (ind_cam // 2)][0], prism[0][1], avg[2]])

        v1 = normalise(cam_pos - cam_front_pos)
        self.cam.cam[-1].camera_pos = cam_pos + 3 * v1
        angle = -angleBetweenVectors(self.cam.cam[-1].camera_front, -v1)
        v3 = normalise(np.cross(self.cam.cam[-1].camera_front, -v1)) * math.sin(angle / 2)
        quat = pyrr.matrix44.create_from_quaternion([v3[0], v3[1], v3[2], math.cos(angle / 2)])
        self.cam.cam[-1].rotateCam(quat)

    def checkDataEntry(self, index):
        # Проверка на ввод информации об объектах
        if "Screen" in self.widgets[index].ui.groupBox.title():
            text = self.widgets[index].ui.radius_object.text()

            radius_flag = setStyleTextObject(self.widgets[index].ui.radius_object, text)

            if radius_flag:
                return True
        else:
            r_text = self.widgets[index].ui.radius_object.text()
            ax_text = self.widgets[index].ui.axis_displacement.text()

            radius_flag = setStyleTextObject(self.widgets[index].ui.radius_object, r_text)
            axis_flag = setStyleTextObject(self.widgets[index].ui.axis_displacement, ax_text)

            if radius_flag and axis_flag:
                return True
        return False

    def counter(self, array, e):
        return max(array.count(e - 1), array.count(e), array.count(e + 1))

    def changeTitle(self, text):
        _translate = QtCore.QCoreApplication.translate
        self.ui.name_window.setHtml(
            _translate("MainWindow", self.ui.text['name_window_part_1'] + text + self.ui.text['name_window_part_2']))

    def initializeGL(self):
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(self.coef_clear_color[0], self.coef_clear_color[1], self.coef_clear_color[2], 1.0)

        glFrustum(0, self.ui.WIDTH_SCREEN, self.ui.HEIGHT_SCREEN, 0, 2, 10)
        glTranslate(self.ui.WIDTH_SCREEN / 2, self.ui.HEIGHT_SCREEN / 2, -2)
        self.loadTexture()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

    def paintGL(self):
        self.list_draw_functions[self.index_paint]()

    def drawAmbiguityLinesAndArrowsOnProjections(self):
        # Отрисовка двух видов и перпендикулярных линий к общей оси в каждом уникальном значении
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.current_key = None
        for i in range(2):
            glPushMatrix()
            glLoadIdentity()
            glFrustum(-self.ui.WIDTH_SCREEN / 2, self.ui.WIDTH_SCREEN / 2, self.ui.HEIGHT_SCREEN / 2,
                      -self.ui.HEIGHT_SCREEN / 2, 2, 10)
            glTranslate(0, 0, -2)
            tmp = np.array(self.laser.points[i])[:, 0]
            border_x = [np.min(tmp), np.max(tmp)]
            tmp = np.array(self.laser.points[i])[:, 1]
            border_y = [np.min(tmp), np.max(tmp)]

            k = 1
            while not (border_x[1] - border_x[0] < 200 * (k - 1) + self.ui.WIDTH_SCREEN / 2 and
                       border_y[1] - border_y[0] < 150 * (k - 1) + self.ui.HEIGHT_SCREEN / 3):
                k += 1
            if k > 1:
                if i:
                    glTranslate(-400 - 200 * k - border_x[0] + 100, -300 - 150 * k - border_y[0] + 50, -k)
                else:
                    glTranslate(-border_x[0] + 100, -300 - 150 * k - border_y[0] + 50, -k)
            else:
                glTranslate(200 * (1 - 2 * i), -200, 0)

            arr = np.array(self.laser.points[i], dtype=int)
            tmp_set = []
            # Надо было поместить в отличную от множества переменную, иначе падает
            f = [tmp_set.append(j) for j in arr[:, 0] if j not in tmp_set]
            for el in tmp_set:
                if el is not None:
                    # Отрисовка линий в уникальных значениях общей оси
                    self.draw(GL_LINES, glVertex2fv, [[el, border_y[0]], [el, 150 * k + border_y[0]]],
                              color=[0.7, 0.7, 0.7, 1.0])

            for key, value in self.controversial_points.items():
                self.limiter_size = value

                tmp_arr = np.array([[key, 150 * k + border_y[0] + 10], [key, 150 * k + border_y[0] + 40]])
                arrow_triangle = makeTrianglesForArrows(tmp_arr[0], None, tmp_arr[1], arrow_size=20)

                # Отрисовка вертикальной линии в неоднозначном значении общей оси
                self.draw(GL_LINES, glVertex2fv, [[key, border_y[0]], [key, 150 * k + border_y[0]]],
                          color=[0.5, 0.5, 0.5, 1.])
                # Отрисовка стрелки к этой линии
                self.draw(GL_TRIANGLES, glVertex2fv, arrow_triangle)
                self.draw(GL_LINES, glVertex2fv, tmp_arr)

                if i:
                    self.current_key = key
                break

            for point in self.laser.points[i]:
                drawCircle(point, 10, 50, self.draw_settings['back-point-color'])
                drawCircle(point, 5, 50, self.draw_settings['front-point-color'])
            # Отрисовка линий лазера
            self.draw(GL_LINE_STRIP, glVertex2fv, self.laser.points[i], color=[1., 0., 0., 1.])

            glPopMatrix()

    def drawAmbiguityLeftView(self):
        # Отрисовка конкурирующих точек на виде слева
        arr_top = np.array(self.laser.points[1], dtype=int)
        z_list = list(map(lambda x: x[1], filter(lambda x: abs(x[0] - self.current_key) <= 1, arr_top)))
        arr_front = np.array(self.laser.points[0], dtype=int)
        y_list = list(map(lambda x: x[1], filter(lambda x: abs(x[0] - self.current_key) <= 1, arr_front)))

        glPushMatrix()
        glLoadIdentity()
        glFrustum(-self.ui.WIDTH_SCREEN / 2, self.ui.WIDTH_SCREEN / 2, self.ui.HEIGHT_SCREEN / 2,
                  -self.ui.HEIGHT_SCREEN / 2, 2, 10)
        glTranslate(0, 0, -2)

        points = np.array([[b, a] for a in y_list for b in z_list])
        border_x = [np.min(points[:, 0]), np.max(points[:, 0])]
        border_y = [np.min(points[:, 1]), np.max(points[:, 1])]
        k = 1
        while not (border_x[1] - border_x[0] < 200 * (k - 1) + self.ui.WIDTH_SCREEN / 2 and
                   border_y[1] - border_y[0] < 150 * (k - 1) + self.ui.HEIGHT_SCREEN / 2):
            k += 1
        glTranslate(-(border_x[0] + border_x[1]) / 2, -border_y[0], -k)

        glBegin(GL_LINES)
        glColor3fv(3 * [0.7])
        for i in range(len(y_list)):
            for j in range(len(z_list) - 1):
                glVertex2f(z_list[j], y_list[i])
                glVertex2f(z_list[j + 1], y_list[i])
        for i in range(len(z_list)):
            for j in range(len(y_list) - 1):
                glVertex2f(z_list[i], y_list[j])
                glVertex2f(z_list[i], y_list[j + 1])
        glEnd()

        for point in points:
            drawCircle(point, 15, 50, self.draw_settings['grid-point-color'])

        self.key_points.clear()
        ind_point = 0
        self.key_points.append(points[ind_point])
        for mode in self.laser.lines:
            addition = 1 if mode else len(z_list)
            self.draw(GL_LINES, glVertex2fv, [points[ind_point], points[ind_point + addition]], color=[0.7, 0.7, 0.7, 1.0])
            ind_point += addition
            self.key_points.append(points[ind_point])

        drawCircle(points[-1], self.draw_settings['cur-tar-point-size'], self.draw_settings['accuracy'],
                   self.draw_settings['target-point-color'])
        drawCircle(points[ind_point], self.draw_settings['cur-tar-point-size'], self.draw_settings['accuracy'],
                   self.draw_settings['current-point-color'])
        glPopMatrix()

    def drawTextData(self, text, **kwargs):
        # Отрисовка текстовой информации
        glPushMatrix()
        k = 1.25
        glColor3f(self.coef_clear_color[0] * k, self.coef_clear_color[1] * k, self.coef_clear_color[2] * k)
        if kwargs['mode'] is "Distance":
            glTranslate(kwargs['translate'][0] - 15 * math.cos(kwargs['angle']) + 5 * (1 - math.cos(kwargs['angle'])),
                        kwargs['translate'][1] + 5 * math.sin(kwargs['angle']) + 10 * (1 - math.sin(kwargs['angle'])),
                        0)
            glRotatef(-math.degrees(kwargs['angle']), 0, 0, 1)
            glScale(kwargs['scale'], kwargs['scale'], 1)
        elif kwargs['mode'] is "Angle":
            offset = kwargs['point_st'] + 50 * kwargs['vector']
            glTranslate(offset[0] + np.sign(kwargs['vector'][0]) * 3 * len(text),
                        offset[1] - np.sign(kwargs['vector'][1]) * 3 * len(text), 0)
            glScale(kwargs['scale'], kwargs['scale'], 1)
        else:
            glScale(20, 20, 1)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        ch_size = 1 / 16

        for elem in text:
            c = ord(elem)
            x = c & 0b1111
            y = c // 16

            self.tex_coord[0] = self.tex_coord[6] = x * ch_size
            self.tex_coord[2] = self.tex_coord[4] = self.tex_coord[0] + ch_size * 0.6
            self.tex_coord[1] = self.tex_coord[3] = y * ch_size
            self.tex_coord[5] = self.tex_coord[7] = self.tex_coord[1] + ch_size
            self.vertex[2] = self.vertex[4] = 0.6
            glVertexPointer(2, GL_FLOAT, 0, self.vertex)
            glTexCoordPointer(2, GL_FLOAT, 0, self.tex_coord)

            glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

            glTranslatef(0.6, 0, 0)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glBindTexture(GL_TEXTURE_2D, 0)

        glPopMatrix()

    def draw(self, mode, func, points, color=None):
        # Абстрактный метод отрисовки
        if color is None:
            color = [0., 0., 0., 1.]
        glBegin(mode)
        glColor4fv(color)
        for point in points:
            func(point)
        glEnd()

    def drawDistanceLines(self, index, angle, arrow_triangles):
        # Отрисовка стрелок и линий к расстоянию между точками
        glPushMatrix()
        self.draw(GL_LINES, glVertex2fv, [self.laser.points[self.state_view][index],
                                          [self.laser.points[self.state_view][index][0] + 20 * math.sin(angle),
                                           self.laser.points[self.state_view][index][1] + 20 * math.cos(angle)],
                                          self.laser.points[self.state_view][index + 1],
                                          [self.laser.points[self.state_view][index + 1][0] + 20 * math.sin(angle),
                                           self.laser.points[self.state_view][index + 1][1] + 20 * math.cos(angle)]],
                                            color=[0.5, 0.5, 0.5, 1.0])

        glTranslate(15 * math.sin(angle), 15 * math.cos(angle), 0)

        self.draw(GL_LINE_STRIP, glVertex2fv,
                  [[self.laser.points[self.state_view][index]], [self.laser.points[self.state_view][index + 1]]],
                  color=[0.5, 0.5, 0.5, 1.])
        self.draw(GL_TRIANGLES, glVertex2fv, arrow_triangles, color=[0.5, 0.5, 0.5, 1.])

        glPopMatrix()

    def drawDistanceData(self, index):
        # Отрисовка расстояния между точками на текущем виде
        avg_point = makeListAvgValue(self.laser.points[self.state_view][index],
                                     self.laser.points[self.state_view][index + 1])

        v_start = np.array(self.laser.points[self.state_view][index])
        v1 = v_start - np.array(self.laser.points[self.state_view][index + 1])
        angle = angleBetweenVectors(v1, np.array([1, 0]))
        if abs(angle - math.pi) > 1e-5:
            if angle >= math.pi / 2:
                while not -math.pi / 2 <= angle <= math.pi / 2:
                    angle -= math.pi
            if angle <= -math.pi / 2:
                while not -math.pi / 2 <= angle <= math.pi / 2:
                    angle += math.pi

        self.drawDistanceLines(index, angle,
                               makeTrianglesForArrows(v_start, np.array(self.laser.points[self.state_view][index + 1]), np.array(avg_point)))

        self.drawTextData(str(int(self.laser.distance_list[self.state_view][index])), angle=angle, mode="Distance",
                          translate=avg_point,
                          scale=20 if int(self.laser.distance_list[self.state_view][index]) > 1500 else 15)

    def drawAngleData(self, index):
        # Отрисовка значения угла на текущем виде
        v_start = np.array(self.laser.points[self.state_view][index])
        v1 = v_start - np.array(self.laser.points[self.state_view][index + 1])
        v2 = np.array(self.laser.points[self.state_view][index - 1]) - v_start
        angle_v = int(round(math.degrees(angleBetweenVectors(-v1, v2))))
        if 0 < angle_v < 180:
            self.drawTextData(str(angle_v) + chr(176), mode="Angle", point_st=v_start,
                              vector=normalise(normalise(v2) - 1.5 * normalise(v1)), scale=16)
            A = np.transpose(np.array([-v1, v2]))
            glBegin(GL_LINES)
            glColor3fv(3 * [0.5])
            for i in range(self.draw_settings['accuracy'] + 1):
                vec = np.array([math.cos(i * 2 * math.pi / self.draw_settings['accuracy']),
                                math.sin(i * 2 * math.pi / self.draw_settings['accuracy'])])
                point = v_start + 30 * vec
                x = np.linalg.solve(A, vec)
                if x[0] >= 0 and x[1] >= 0:
                    glVertex2fv(point)
            glEnd()

    def drawFlickeringSpheres(self):
        # Отрисовка сфер для ориентации пользователя о вбитых данных
        quad = gluNewQuadric()
        model_loc = glGetUniformLocation(self.shader, "model")
        color_loc = glGetUniformLocation(self.shader, "color_vec")
        button_flag = True

        self.t += self.sign * 0.00015
        for i in range(1, len(self.laser.total_3D_points)):
            model = pyrr.matrix44.create_from_translation(self.laser.total_3D_points[i])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
            check = self.checkDataEntry(i - 1)
            button_flag &= check
            if check:
                color = pyrr.Vector4([0., 1., 0., 0.5])
            else:
                color = pyrr.Vector4([1., 0., 0., 0.5])
            glUniform4fv(color_loc, 1, color)
            gluSphere(quad, self.t, 20, 20)

        self.ui.save_model_in_result_tab.setEnabled(button_flag)

        if self.t > 0.05:
            self.sign = -1
        elif self.t < 0.005:
            self.sign = 1

    def loadViews(self):
        # Отрисовка сцены с одним из видов
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        offset = np.mean(np.array(self.laser.points[self.state_view]), axis=0)

        glPushMatrix()
        max_k = 0
        for point in self.laser.points[self.state_view]:
            k = 0
            while not -self.ui.WIDTH_SCREEN / 2 <= point[0] - (k + 1) * offset[0] <= self.ui.WIDTH_SCREEN / 2 or \
                    not -self.ui.HEIGHT_SCREEN / 2 <= point[1] - (k + 1) * offset[1] <= self.ui.HEIGHT_SCREEN / 2:
                k += 1
            max_k = max(max_k, k)

        glTranslate(-(max_k + 1) * offset[0], -(max_k + 1) * offset[1], -max_k)

        for i in range(len(self.laser.points[self.state_view]) - 1):
            self.drawDistanceData(i)
            if i > 0:
                self.drawAngleData(i)

        for point in self.laser.points[self.state_view]:
            drawCircle(point, self.draw_settings['back-point-size'], self.draw_settings['accuracy'],
                       self.draw_settings['back-point-color'])
            drawCircle(point, self.draw_settings['front-point-size'], self.draw_settings['accuracy'],
                       self.draw_settings['front-point-color'])

        self.draw(GL_LINE_STRIP, glVertex2fv, self.laser.points[self.state_view], color=[1., 0., 0., 1.])

        glPopMatrix()
        glFlush()

    def loadControversialCase(self):
        # Отрисовка сцены с конкурирующими точками
        self.drawAmbiguityLinesAndArrowsOnProjections()

        if self.current_key is not None:
            self.drawAmbiguityLeftView()

    def load3DScene(self):
        # Отрисовка сцены с 3D моделью
        self.findLookoutPoint()

        self.shader = compileProgram(compileShader(self.vertex_src, GL_VERTEX_SHADER),
                                     compileShader(self.fragment_src, GL_FRAGMENT_SHADER))

        glUseProgram(self.shader)
        glClearColor(self.coef_clear_color[0], self.coef_clear_color[1], self.coef_clear_color[2], 1.0)
        glEnable(GL_DEPTH_TEST)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        proj_loc = glGetUniformLocation(self.shader, "projection")
        view_loc = glGetUniformLocation(self.shader, "view")
        model_loc = glGetUniformLocation(self.shader, "model")

        view = self.cam.getViewMatrix()
        projection = pyrr.matrix44.create_perspective_projection_matrix(45,
                                                                        self.ui.WIDTH_SCREEN / self.ui.HEIGHT_SCREEN,
                                                                        0.01, 700)
        model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0., 0., 0.]))

        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

        # Отрисовка лазера
        self.draw(GL_LINE_STRIP, glVertex3fv, self.laser.total_3D_points)
        self.drawFlickeringSpheres()

        self.ui.openGLWidget.update()

    def loadTexture(self):
        # Загрузка текстуры с символами
        f = open(TEXTURE_SYMBOLS, "rb")
        img = Image.open(f)
        pix = img.load()
        for x in range(img.width):
            for y in range(img.height):
                if pix[x, y] == (255, 255, 255, 255):
                    pix[x, y] = (0, 0, 0, 255)
                else:
                    pix[x, y] = (0, 0, 0, 0)
        img_data = img.tobytes()
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        glBindTexture(GL_TEXTURE_2D, 0)

    def addObjectsToList(self):
        # Метод отвечает за добавление предметов в оптический путь лазера
        points = np.array(self.laser.total_3D_points)

        self.widgets.append(ObjectWidget())
        self.ui.objects_layout.addWidget(self.widgets[-1], QtCore.Qt.AlignBottom)
        index_screens = [len(points) - 1]

        for i in range(len(points) - 2, 0, -1):
            self.widgets.append(ObjectWidget())
            self.ui.objects_layout.addWidget(self.widgets[-1], QtCore.Qt.AlignBottom)

            v1 = points[i] - points[i - 1]
            v2 = points[i + 1] - points[i]
            if angleBetweenVectors(v1, v2) < 1e-3:
                index_screens.append(i)

        number_screen = number_mirror = 1
        for i in range(1, len(points)):
            if i in index_screens:
                self.widgets[i - 1].set_type("Screen #" + str(number_screen))
                number_screen += 1
            else:
                self.widgets[i - 1].set_type("Mirror #" + str(number_mirror))
                number_mirror += 1

    def addPoint(self):
        # Данный метод отвечает за проверку текстовых полей и добавление точки к текущему виду
        angle_text = self.ui.angle_input.text()
        distance_text = self.ui.distance_input.text()
        if not is_number(angle_text) or not is_number(distance_text):
            self.ui.angle_text_box.setStyleSheet('color: red')
            self.ui.distance_text_box.setStyleSheet('color: red')
        else:
            angle = math.radians(float(angle_text))
            distance = float(distance_text)
            self.laser.distance_list[self.state_view].append(distance)
            self.laser.points[self.state_view].append(
                [self.laser.points[self.state_view][-1][0] + distance / 10 * math.sin(angle),
                 self.laser.points[self.state_view][-1][1] - distance / 10 * math.cos(angle)])
            self.ui.angle_text_box.setStyleSheet('color: white')
            self.ui.distance_text_box.setStyleSheet('color: white')
            self.ui.openGLWidget.update()
        self.ui.angle_input.clear()
        self.ui.distance_input.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px solid white; }")
    mainWindow = QtWidgets.QMainWindow()
    ui = MainWindow(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
