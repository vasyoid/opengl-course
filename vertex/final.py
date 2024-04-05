from math import sqrt

import pygame

from OpenGL.GL import *


def draw_triangle():
    glBegin(GL_TRIANGLES)
    glColor(255, 0, 0)
    glVertex(-0.5, -1 / (2 * sqrt(3)))
    glColor(0, 255, 0)
    glVertex(0.5, -1 / (2 * sqrt(3)))
    glColor(0, 0, 255)
    glVertex(0,  1 / sqrt(3))
    glEnd()

def main():
    pygame.init()
    width = 800
    height = 800
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        glClear(GL_COLOR_BUFFER_BIT)
        draw_triangle()

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    main()
