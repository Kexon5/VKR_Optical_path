from pyrr import matrix44, quaternion
from math import sin, cos, radians, acos, asin, degrees
from utils import *

ZOOM_MIN = 1.0
ZOOM_MAX = 45.


class CameraControl:
    class Camera:
        def __init__(self, **kwargs):
            self.camera_pos = np.array([0.0, 0.0, 0.0]) if "pos" not in kwargs else np.array(kwargs['pos'])
            self.camera_front = np.array([0.0, 0.0, 1.0]) if "front" not in kwargs else np.array(kwargs['front'])
            self.camera_up = np.array([0.0, 1.0, 0.0]) if "up" not in kwargs else np.array(kwargs['up'])
            self.camera_right = np.array([-1.0, 0.0, 0.0]) if "right" not in kwargs else np.array(kwargs['right'])

            self.mouse_sensitivity = 0.25
            self.zoom = 45.
            self.pitch = degrees(asin(self.camera_front[1]))

            if self.pitch > 80:
                self.pitch = 80
            if self.pitch < -80:
                self.pitch = -80

            jaw_asin = asin(self.camera_front[2] / cos(radians(self.pitch)))
            sol_sin = [jaw_asin, -jaw_asin + math.pi]
            jaw_acos = acos(self.camera_front[0] / cos(radians(self.pitch)))
            sol_cos = [jaw_acos, -jaw_acos]
            for el1 in sol_cos:
                for el2 in sol_sin:
                    if abs(el1 - el2) < 1E-6:
                        self.jaw = degrees(el1)

            self.default_camera_pos = self.camera_pos.copy()
            self.default_camera_front = self.camera_front.copy()
            self.default_camera_up = self.camera_up.copy()
            self.default_camera_right = self.camera_right.copy()
            self.default_zoom = self.zoom
            self.default_pitch = self.pitch
            self.default_jaw = self.jaw

        def saveState(self):
            self.default_camera_pos = self.camera_pos.copy()
            self.default_camera_front = self.camera_front.copy()
            self.default_camera_up = self.camera_up.copy()
            self.default_camera_right = self.camera_right.copy()
            self.default_zoom = self.zoom
            self.default_pitch = self.pitch
            self.default_jaw = self.jaw

        def backSavePosition(self):
            self.camera_pos = self.default_camera_pos.copy()
            self.camera_front = self.default_camera_front.copy()
            self.camera_up = self.default_camera_up.copy()
            self.camera_right = self.default_camera_right.copy()
            self.zoom = self.default_zoom
            self.pitch = self.default_pitch
            self.jaw = self.default_jaw

        def getViewMatrix(self):
            return matrix44.create_look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

        def processMouseMovement(self, xoffset, yoffset, constrain_pitch=True):
            xoffset *= self.mouse_sensitivity
            yoffset *= self.mouse_sensitivity

            self.jaw += xoffset
            self.pitch += yoffset

            if constrain_pitch:
                if self.pitch > 85:
                    self.pitch = 85
                if self.pitch < -85:
                    self.pitch = -85

            self.updateCameraVectors()

        def processScroll(self, yoffset):
            if ZOOM_MIN <= self.zoom <= ZOOM_MAX:
                self.zoom -= yoffset
            if self.zoom <= ZOOM_MIN:
                self.zoom = ZOOM_MIN
            if self.zoom >= ZOOM_MAX:
                self.zoom = ZOOM_MAX

        def updateCameraVectors(self):
            front = np.array([0.0, 0.0, 0.0])
            front[0] = cos(radians(self.jaw)) * cos(radians(self.pitch))
            front[1] = sin(radians(self.pitch))
            front[2] = sin(radians(self.jaw)) * cos(radians(self.pitch))

            self.camera_front = normalise(front)
            self.camera_right = np.cross(self.camera_front, np.array([0.0, 1.0, 0.0]))
            self.camera_up = np.cross(self.camera_right, self.camera_front)

        def setPitchAndJaw(self):
            self.pitch = degrees(asin(self.camera_front[1]))

            if self.pitch > 85:
                self.pitch = 85
            if self.pitch < -85:
                self.pitch = -85

            jaw_asin = asin(self.camera_front[2] / cos(radians(self.pitch)))
            sol_sin = [jaw_asin, -jaw_asin + math.pi]
            jaw_acos = acos(self.camera_front[0] / cos(radians(self.pitch)))
            sol_cos = [jaw_acos, -jaw_acos]
            for el1 in sol_cos:
                for el2 in sol_sin:
                    if abs(el1 - el2) < 1E-6:
                        self.jaw = degrees(el1)

        def rotateCam(self, quat=quaternion):
            self.camera_front = matrix44.apply_to_vector(quat, np.append(self.camera_front, 0.))[:3]
            self.camera_right = np.cross(self.camera_front, np.array([0.0, 1.0, 0.0]))
            self.camera_up = np.cross(self.camera_right, self.camera_front)

            self.setPitchAndJaw()


        def processKeyboard(self, direction, velocity):
            if direction == "FORWARD":
                self.camera_pos += self.camera_front * velocity
            if direction == "BACKWARD":
                self.camera_pos -= self.camera_front * velocity
            if direction == "LEFT":
                self.camera_pos -= self.camera_right * velocity
            if direction == "RIGHT":
                self.camera_pos += self.camera_right * velocity
            if direction == "SPACE":
                self.camera_pos += np.array([0., 1., 0.]) * velocity
            if direction == "SHIFT":
                self.camera_pos -= np.array([0., 1., 0.]) * velocity

    def __init__(self, **kwargs):
        self.cam = [CameraControl.Camera(**kwargs)]
        self.current_cam = 0

    def setCam(self, index):
        if index < len(self.cam):
            self.current_cam = index

    def setCamSettings(self, cam_data_dict):
        self.cam[self.current_cam].camera_pos = np.array(cam_data_dict['cam_pos'])
        self.cam[self.current_cam].camera_front = np.array(cam_data_dict['cam_front'])
        self.cam[self.current_cam].camera_up = np.array(cam_data_dict['cam_up'])
        self.cam[self.current_cam].camera_right = np.array(cam_data_dict['cam_right'])

        self.cam[self.current_cam].setPitchAndJaw()
        self.cam[self.current_cam].saveState()

    def getZoom(self):
        return self.cam[self.current_cam].zoom

    def nextCam(self):
        self.current_cam = self.current_cam + 1 if self.current_cam + 1 < len(self.cam) else 0

    def addCamera(self, **kwargs):
        self.cam.append(CameraControl.Camera(**kwargs))

    def backSavePosition(self):
        self.cam[self.current_cam].backSavePosition()

    def printInfo(self):
        print("Camera number: ", self.current_cam)
        print("Direction camera:")
        print(self.cam[self.current_cam].camera_front)

    def addCamerasForGlasses(self, objects):
        for i in range(1, len(objects) - 2):
            v1 = objects[i - 1].point - objects[i].point
            v2 = objects[i + 1].point - objects[i].point

            v = normalise(np.cross(v1, v2))
            if 1 - 1E-5 <= abs(v[1]) <= 1 + 1E-5:
                v = normalise(v + objects[i].normal)

            self.addCamera()
            self.cam[-1].camera_pos = objects[i].point + v * 0.2
            angle = -angleBetweenVectors(self.cam[-1].camera_front, -v)
            v3 = normalise(np.cross(self.cam[-1].camera_front, -v)) * math.sin(angle / 2)
            quat = matrix44.create_from_quaternion([v3[0], v3[1], v3[2], math.cos(angle / 2)])
            self.cam[-1].rotateCam(quat)
            self.cam[-1].saveState()

    def getViewMatrix(self):
        return self.cam[self.current_cam].getViewMatrix()

    def processMouseMovement(self, xoffset, yoffset, constrain_pitch=True):
        self.cam[self.current_cam].processMouseMovement(xoffset, yoffset, constrain_pitch)

    def processScroll(self, yoffset):
        self.cam[self.current_cam].processScroll(yoffset)

    def updateCameraVectors(self):
        self.cam[self.current_cam].updateCameraVectors()

    def rotateCam(self, quat):
        self.cam[self.current_cam].rotateCam(quat)

    def processKeyboard(self, direction, velocity):
        self.cam[self.current_cam].processKeyboard(direction, velocity)
