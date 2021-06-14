import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pyrr
import math
from utils import *


class ObjectOPV:
    def __init__(self, type_obj, point, radius, axis=None):
        self.type_obj = type_obj
        self.point = point
        self.radius = radius
        self.accuracy = 50
        self.cyl = gluNewQuadric()
        self.normal = None
        if axis is not None:
            self.axis = axis

    def getType(self):
        return self.type_obj

    def getNormal(self):
        return self.normal

    def draw(self, shader):
        model_loc = glGetUniformLocation(shader, "model")
        m1 = pyrr.matrix44.create_from_translation(self.point)


        v_z = np.array([0., 0., 1.0])
        v3 = normalise(np.cross(self.normal, v_z))

        m2 = pyrr.matrix44.create_from_quaternion([v3[0], v3[1], v3[2], -angleBetweenVectors(self.normal, v_z)])
        model = pyrr.matrix44.multiply(m2, m1)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        color_loc = glGetUniformLocation(shader, "ourColor")
        color = pyrr.Vector4([0., 0., 0., 1.])
        glUniform4fv(color_loc, 1, color)
        gluCylinder(self.cyl, self.radius, self.radius, 0.001, self.accuracy, self.accuracy)
        gluDisk(self.cyl, 0, self.radius, self.accuracy, self.accuracy)
