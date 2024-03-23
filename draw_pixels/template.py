import pygame

from OpenGL.GL import *


def image_to_buffer(image):
    height = len(image)
    width = len(image[0])
    buffer = bytearray(width * height * 3)
    for row in range(height):
        for col in range(width):
            for comp in range(3):
                buffer[row * width * 3 + col * 3 + comp] = image[row][col][comp]
    return buffer


def create_image(width, height):
    return [[(0, 0, 0) for _ in range(width)] for _ in range(height)]


def draw_circle(width, height):
    image = create_image(width, height)

    for row in range(height):
        for col in range(width):
            x = col * 2 / width - 1
            y = -row * 2 / height + 1


    buffer = image_to_buffer(image)
    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, buffer)


def main():
    pygame.init()
    width = 600
    height = 600
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_LEFT:
                    pass
                if event.key == pygame.K_RIGHT:
                    pass
                if event.key == pygame.K_DOWN:
                    pass
                if event.key == pygame.K_UP:
                    pass

        glClear(GL_COLOR_BUFFER_BIT)

        draw_circle(width, height)

        pygame.display.flip()
        pygame.time.wait(10)


main()
