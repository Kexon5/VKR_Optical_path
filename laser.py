import pyrr
from utils import *
from objectOPV import ObjectOPV
from OpenGL.GLU import *
import random

class Laser:
    def __init__(self, objects):
        #self.points = np.array([ 0., 0., 0.], dtype=np.float32)
        self.points = np.array(objects[0].point, dtype=np.float32)
        self.objects = objects
        self.default_normal = normalise(objects[1].point - objects[0].point)
        self.current_normal = self.default_normal.copy()
        self.positions = pyrr.Vector3([0., 0., 0.])
        self.passing_screen = 2 * [False]
        self.VBO = glGenBuffers(1)
        self.num = 0
        self.fix_flag = False
        self.normals = None
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.acceptNormalPosition()

    def acceptNormalPosition(self):
        for i in range(1, len(self.objects) - 2):
            v1 = normalise(self.objects[i].point - self.objects[i - 1].point)
            v2 = normalise(self.objects[i + 1].point - self.objects[i].point)
            self.objects[i].normal = normalise(v2 - v1)

        for i in range(len(self.objects) - 2, len(self.objects)):
            self.objects[i].normal = np.array([-1., 0., 0.])

    def add_point(self, point):
        self.points = np.append(self.points, point, axis=0)

    def intersect(self):
        self.points = np.array(self.objects[0].point, dtype=np.float32)
        self.current_normal = self.default_normal.copy()
        self.passing_screen = 2 * [False]


        error_flag = False
        for i in range(1, len(self.objects)):
            denom = np.dot(self.current_normal, self.normals[i])
            if np.abs(denom) < 1e-6:
                self.add_point(self.current_normal * 10)
                error_flag = True
                break
            if "Mirror" in self.objects[i].type_obj:
                d = np.dot(self.objects[i].point - self.points[3 * (i - 1): 3 * i], self.normals[i]) / denom
                if d < 0:
                    self.add_point(self.current_normal * 10)
                    error_flag = True
                    break

                tmp_point = self.points[3 * (i - 1): 3 * i] + self.current_normal * d
                if distance(tmp_point, self.objects[i].point) < self.objects[i].radius:
                    self.add_point(tmp_point)
                    self.current_normal -= 2 * self.normals[i] * np.dot(self.current_normal, self.normals[i])
                else:
                    self.add_point(self.current_normal * 10)
                    error_flag = True
                    break
            else:
                d = np.dot(self.objects[i].point - self.points[-3:], self.normals[i]) / denom
                if d < 0:
                    self.passing_screen[i - len(self.objects) + 2] = False
                    continue
                tmp_point = self.points[-3:] + self.current_normal * d
                if distance(tmp_point, self.objects[i].point) < self.objects[i].radius:
                    self.passing_screen[i - len(self.objects) + 2] = True
                else:
                    self.passing_screen[i - len(self.objects) + 2] = False
        if not error_flag:
            self.add_point(self.points[-3:] + self.current_normal * 10)

        return error_flag

    def recover_system(self):
        ind_fix = len(self.points) // 3 - 2

        angle = angleBetweenVectors(self.objects[ind_fix].normal, self.normals[ind_fix])
        print(angle)
        if abs(angle) > 0.01:
            angle /= 50
            v = normalise(np.cross(self.objects[ind_fix].normal, self.normals[ind_fix])) * math.sin(angle / 2)

            quat = pyrr.matrix44.create_from_quaternion([v[0], v[1], v[2], math.cos(angle / 2)])
            self.normals[ind_fix] = pyrr.matrix44.apply_to_vector(quat, np.append(self.normals[ind_fix], 0.))[:3]
        else:
            self.normals[ind_fix] = self.objects[ind_fix].normal
            #print(ind_fix)

    def draw(self, shader):
        model_loc = glGetUniformLocation(shader, "model")
        model = pyrr.matrix44.create_from_translation(self.positions)
        color_loc = glGetUniformLocation(shader, "ourColor")
        color = pyrr.Vector4([1., 0., 0., 1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glUniform4fv(color_loc, 1, color)
        # Точка получения текущих нормалей
        if not self.fix_flag:
            self.normals = list(map(ObjectOPV.getNormal, self.objects))
        if self.num:
            v_rand = np.array([random.random(), random.random(), random.random()])
            self.normals[1] = normalise(self.normals[1] + v_rand)
            self.normals[2] = normalise(self.normals[2] + v_rand)
            self.normals[3] = normalise(self.normals[3] + v_rand)
            self.num = 0
        error = self.intersect()
        if error:
            self.fix_flag = True
            self.recover_system()
        else:
            self.fix_flag = False
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.points.nbytes, self.points, GL_DYNAMIC_DRAW)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.points)//3)

        # glDrawElemen(GL_LINE_STRIP, 10, GL_UNSIGNED_INT, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        model_loc = glGetUniformLocation(shader, "model")
        m1 = pyrr.matrix44.create_from_translation(self.objects[-2].point)

        v_z = np.array([0., 0., 1.0])
        v3 = normalise(np.cross(self.objects[-2].normal, v_z))
        # print(v3)
        m2 = pyrr.matrix44.create_from_y_rotation(math.pi/2)
        model = pyrr.matrix44.multiply(m2, m1)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        color_loc = glGetUniformLocation(shader, "ourColor")
        if self.passing_screen[0] and self.passing_screen[1]:
            color = pyrr.Vector4([0., 1., 0., 0.5])
        else:
            color = pyrr.Vector4([0., 0., 0., 0.5])
        glUniform4fv(color_loc, 1, color)
        gluCylinder(self.objects[-2].cyl, 0.007, 0.003, 3.884, 50, 50)

        for i in range(1, len(self.objects) - 2):
            self.objects[i].draw(shader)



