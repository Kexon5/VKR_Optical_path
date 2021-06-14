import math
import pygame
from diplom.utils import *
import numpy as np

class TokamakJumpingModel:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.x0 = 0.
        self.y0 = b
        self.cur_x = 0.
        self.cur_y = 0.
        self.v = 2
        self.s = 0.

    def fun(self, x):
        return self.y0 - self.b * math.sqrt(1 - ((x - self.x0) / self.a) ** 2)

    def dfun(self, x):
        return self.b * (x - self.x0) / math.sqrt(1 - ((x - self.x0) / self.a) ** 2)

    def normal(self, x):
        return -normalise(np.array([(2 * x - 2 * self.x0) / self.a ** 2, (2 * self.fun(x) - 2 * self.y0) / self.b ** 2]))

    def tangent(self, x):
        v1 = np.array([1, self.dfun(x)])
        v2 = np.array([self.x0 - x, self.y0 - self.fun(x)])
        angle = angleBetweenVectors(v1, v2)
        if angle < math.pi/2:
            return v1
        else:
            return -v1

    def angle(self, x):
        v1 = np.array([1, self.dfun(x)])
        v2 = np.array([1, 0.])
        return math.acos(abs(np.sum(v1 * v2) / (np.sum(v1 * v1) * np.sum(v2 * v2)) ** 0.5))

    def draw(self, sc, t):
        sign = 1
        if abs(t) > 1e-6:
            sign = t / abs(t)
            t = abs(t)
        x = max(self.v * t - t ** 2, 0)
        angle = self.angle(x)
        pygame.draw.circle(sc, (255, 0, 0), (400 + sign * 100 * x, 600 - 10 - 200 * abs(self.fun(x))), 10)
        #self.v = max(self.v - 0.00001*t, 0.)
        #print(0.01 * t)


def main():
    pygame.init()
    sc = pygame.display.set_mode((800, 600))
    por = TokamakJumpingModel(2., 1.)
    t = 0.
    sign = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        sc.fill((0, 0, 0))
        por.draw(sc, t)

        t += 0.0001 * sign
        if t > 1 or t < -1:
            sign *= -1
        #pygame.time.delay(20)
        pygame.display.update()



if __name__ == "__main__":
    main()