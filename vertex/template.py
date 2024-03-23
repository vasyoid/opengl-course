import pygame

from OpenGL.GL import *


def draw_triangle():
    pass

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
