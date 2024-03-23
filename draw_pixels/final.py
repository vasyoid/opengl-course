import math

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


def draw_circle(width, height, w, s):
    image = create_image(width, height)

    for row in range(height):
        for col in range(width):
            x = col * 2 / width - 1
            y = row * 2 / height - 1

            d = abs(x ** 2 + y ** 2 - 0.5 ** 2)
            if d <= w:
                color = 255
            elif d <= w + s:
                color = int(255 - 255 * (d - w) / s)
            else:
                color = 0

            image[row][col] = (color, color, color)

    buffer = image_to_buffer(image)
    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, buffer)


def draw_rgb(width, height):
    image = create_image(width, height)

    for row in range(height):
        for col in range(width):
            x = col * 2 / width - 1
            y = row * 2 / height - 1

            d1 = x ** 2 + (y - math.sqrt(2) / 3) ** 2
            red = max(0, int(255 - 255 * d1 / 0.6))

            d2 = (x - 0.5) ** 2 + (y + 1 / math.sqrt(2) / 3) ** 2
            green = max(0, int(255 - 255 * d2 / 0.6))

            d3 = (x + 0.5) ** 2 + (y + 1 / math.sqrt(2) / 3) ** 2
            blue = max(0, int(255 - 255 * d3 / 0.6))

            image[row][col] = (red, green, blue)

    buffer = image_to_buffer(image)
    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, buffer)


def main():
    pygame.init()
    width = 800
    height = 800
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)

    w = 0.005
    s = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_LEFT:
                    w = max(0.005, w - 0.005)
                if event.key == pygame.K_RIGHT:
                    w += 0.005
                if event.key == pygame.K_DOWN:
                    s = max(0, s - 0.005)
                if event.key == pygame.K_UP:
                    s += 0.005

        glClear(GL_COLOR_BUFFER_BIT)

        draw_rgb(width, height)

        pygame.display.flip()
        pygame.time.wait(10)


main()
