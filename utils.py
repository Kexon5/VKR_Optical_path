import json

from OpenGL.GL import *
import numpy as np
import math


def setStyleTextObject(obj, text):
    if text:
        if is_number(text):
            obj.setStyleSheet('color: white')
            return True
        else:
            obj.setStyleSheet('color: red')
    else:
        obj.setStyleSheet('color: white')
    return False


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def makeListAvgValue(v1, v2):
    vec_list = [0.] * len(v1)
    for i in range(len(v1)):
        vec_list[i] = (v1[i] + v2[i]) / 2
    return vec_list


def distance(v1, v2):
    return np.sqrt(np.sum(np.square(v1-v2)))

def makeTrianglesForArrows(v1, v2, v_avg, arrow_size=10):
    tmp = normalise(v1 - v_avg)
    vP1 = normalise(tmp + 0.5 * np.array([-tmp[1], tmp[0]]))
    vP2 = normalise(tmp + 0.5 * np.array([tmp[1], -tmp[0]]))

    if v2 is not None:
        tmp = normalise(v2 - v_avg)
        vP3 = normalise(tmp + 0.5 * np.array([-tmp[1], tmp[0]]))
        vP4 = normalise(tmp + 0.5 * np.array([tmp[1], -tmp[0]]))
        return [v1, v1 + (-arrow_size) * vP1, v1 + (-arrow_size) * vP2,
                v2, v2 + (-arrow_size) * vP3, v2 + (-arrow_size) * vP4]
    else:
        return [v1, v1 + (-arrow_size) * vP1, v1 + (-arrow_size) * vP2]


def angleBetweenVectors(v1, v2):
    val_cos = np.sum(v1 * v2) / (np.sum(v1 * v1) * np.sum(v2 * v2)) ** 0.5
    if val_cos > 1:
        val_cos = 1
    elif val_cos < -1:
        val_cos = -1
    return math.acos(val_cos)


def normalise(v):
    return v / np.sum(v * v) ** 0.5


def drawCircle(point, radius, accuracy, color):
    glBegin(GL_TRIANGLE_FAN)
    glColor4fv(color)
    glVertex2fv(point)
    for i in range(accuracy + 1):
        glVertex2f(point[0] + (radius * math.cos(i * 2 * math.pi / accuracy)),
                   point[1] + (radius * math.sin(i * 2 * math.pi / accuracy)))
    glEnd()


def checkFile(file_name, returnDict=False):
    with open(file_name, "r") as jsonIn:
        strData = jsonIn.read()
    tmp_dict = json.loads(strData)

    count_starts = count_mirrors = count_screens = count_cameras = 0
    invalid_file_flag = False
    for key, items in tmp_dict.items():
        if "Camera" in key:
            if "cam_pos" in tmp_dict[key] and type(tmp_dict[key]["cam_pos"]) is list and\
                    "cam_front" in tmp_dict[key] and type(tmp_dict[key]["cam_front"]) is list and\
                    "cam_up" in tmp_dict[key] and type(tmp_dict[key]["cam_up"]) is list and\
                    "cam_right" in tmp_dict[key] and type(tmp_dict[key]["cam_right"]) is list:
                count_cameras += 1
                continue
            else:
                invalid_file_flag = True
                break

        if "Start" in key and "point" in tmp_dict[key] and type(tmp_dict[key]["point"]) is list:
            count_starts += 1
            continue
        if "Mirror #" in key:
            if "point" in tmp_dict[key] and "radius" in tmp_dict[key] and "displacement" in tmp_dict[key] and \
                    type(tmp_dict[key]["radius"]) is float and type(tmp_dict[key]["displacement"]) is float and \
                    type(tmp_dict[key]["point"]) is list:
                count_mirrors += 1
                continue
            else:
                invalid_file_flag = True
                break
        if "Screen #" in key:
            if "point" in tmp_dict[key] and "radius" in tmp_dict[key] and \
                    type(tmp_dict[key]["radius"]) is float and type(tmp_dict[key]["point"]) is list:
                count_screens += 1
            else:
                invalid_file_flag = True
                break

    if not invalid_file_flag and count_starts == 1 and count_mirrors >= 1 and count_screens == 2 and count_cameras == 1:
        return True, tmp_dict if returnDict else True
    else:
        return False, None if returnDict else False