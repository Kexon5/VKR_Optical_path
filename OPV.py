import sys
import time

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pyrr
from camera import CameraControl
from laser import Laser
import numpy as np
from objectOPV import ObjectOPV
from utils import *

DEFAULT_NAME = "Optical Path Viewer"
VERTEX_SHADER = 'res\\shaders\\OPV.vert'
FRAGMENT_SHADER = 'res\\shaders\\OPV.frag'
mov = 0
cam = CameraControl()
objects = []
left, right, forward, backward, space, shift = False, False, False, False, False, False
first_mouse = True
WIDTH = 800
HEIGHT = 600

vertex_src = open(VERTEX_SHADER, "rb").read()
fragment_src = open(FRAGMENT_SHADER, "rb").read()


def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
    proj_loc = glGetUniformLocation(shader, "projection")
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


def scroll_callback(window, xoffset, yoffset):
    cam.processScroll(yoffset)


def key_callback(window, key, scancode, action, mode):
    global left, right, forward, backward, space, shift, mov
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_1 and action == glfw.PRESS:
        cam.nextCam()
        if cam.current_cam:
            glfw.set_window_title(window, DEFAULT_NAME + " | Mirror #" + str(cam.current_cam))
        else:
            glfw.set_window_title(window, DEFAULT_NAME + " | General view")

    if key == glfw.KEY_2 and action == glfw.PRESS:
        cam.backSavePosition()

    if key == glfw.KEY_9 and action == glfw.PRESS:
        if cam.current_cam:
            print(str(cam.current_cam) + " mirror normal:\n")
            print(objects[cam.current_cam].normal)
        else:
            for i in range(1, len(objects) - 2):
                print(str(i) + " mirror normal:\n")
                print(objects[i].normal)

    if key == glfw.KEY_0 and action == glfw.PRESS:
        cam.printInfo()

    if key == glfw.KEY_4 and action == glfw.PRESS:
        mov = 1

    if key == glfw.KEY_W and action == glfw.PRESS:
        forward = True
    if key == glfw.KEY_S and action == glfw.PRESS:
        backward = True
    if key == glfw.KEY_A and action == glfw.PRESS:
        left = True
    if key == glfw.KEY_D and action == glfw.PRESS:
        right = True
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        space = True
    if key == glfw.KEY_LEFT_SHIFT and action == glfw.PRESS:
        shift = True
    if key in [glfw.KEY_W, glfw.KEY_S, glfw.KEY_D, glfw.KEY_A, glfw.KEY_SPACE, glfw.KEY_LEFT_SHIFT] and action == glfw.RELEASE:
        left, right, forward, backward, space, shift = False, False, False, False, False, False


def do_movement(delta_time):
    if left:
        cam.processKeyboard("LEFT", delta_time)
    if right:
        cam.processKeyboard("RIGHT", delta_time)
    if forward:
        cam.processKeyboard("FORWARD", delta_time)
    if backward:
        cam.processKeyboard("BACKWARD", delta_time)
    if space:
        cam.processKeyboard("SPACE", delta_time)
    if shift:
        cam.processKeyboard("SHIFT", delta_time)


def mouse_look_callback(window, xpos, ypos):
    global first_mouse, lastX, lastY

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS and not first_mouse:
        xoffset = xpos - lastX
        yoffset = lastY - ypos

        cam.processMouseMovement(xoffset, yoffset)

    lastX = xpos
    lastY = ypos


def main(data):
    global shader, mov
    delta_time = 0.
    last_frame = 0.

    if not glfw.init():
        return

    window = glfw.create_window(WIDTH, HEIGHT, DEFAULT_NAME + " | General view", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_window_size_callback(window, window_resize)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_look_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    info = {"objects": [{"point": np.array([0.0, 0.0, 0.0], dtype=np.float32), "type": "Start", "radius": 0.007},
                         {"point": np.array([0.0, 1.0, 0.0], dtype=np.float32), "type": "Mirror", "radius": 0.007},
                         {"point": np.array([-1.334, 1.0, 0.48], dtype=np.float32), "type": "Mirror", "radius": 0.007},
                         {"point": np.array([-1.334, 1.0, -2.71], dtype=np.float32), "type": "Mirror", "radius": 0.007},
                         {"point": np.array([-1.334, 2.75, -2.71], dtype=np.float32), "type": "Mirror", "radius": 0.007},
                         {"point": np.array([-4.108760447723849, 2.75, -2.7109111950442935], dtype=np.float32), "type": "Screen", "radius": 0.007},
                         {"point": np.array([-7.99276044772385, 2.75, -2.7109111950442935], dtype=np.float32), "type": "Screen", "radius": 0.003}]}
    #objects = []
    points = None
    for key, value in data.items():
        if "Camera" in key:
            cam.setCamSettings(value)
            continue
        if "Mirror" in key:
            objects.append(ObjectOPV("Mirror", np.array(value['point'], dtype=np.float32), value['radius'], axis=value['displacement']))
        if "Screen" in key:
            objects.append(ObjectOPV("Screen", np.array(value['point'], dtype=np.float32), value['radius']))
        if "Start" in key:
            objects.append(ObjectOPV("Start", np.array(value['point'], dtype=np.float32), 0.))


    las = Laser(objects)
    cam.addCamerasForGlasses(objects)

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    glEnable(GL_DEPTH_TEST)
    glUseProgram(shader)
    glClearColor(0.2, 0.3, 0.3, 1.0)

    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        glfw.poll_events()
        do_movement(delta_time * 2)
        if mov:
            las.num = mov
            mov = 0
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = cam.getViewMatrix()

        projection = pyrr.matrix44.create_perspective_projection_matrix(cam.getZoom(), WIDTH / HEIGHT, 0.1, 100)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        las.draw(shader)
        time.sleep(0.001)
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        flag, data = checkFile(sys.argv[1], returnDict=True)
        if flag:
            main(data)
        else:
            print("Incorrect data")
    else:
        print("Incorrect arguments")
