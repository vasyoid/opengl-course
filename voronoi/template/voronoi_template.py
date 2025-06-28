import random
import time
from ctypes import sizeof, c_void_p
from typing import Tuple

import glfw
import numpy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

width = 800
height = 800

def read_shader_file(filename):
    with open(filename, encoding="UTF-8") as file:
        return "".join(file.readlines())


def init_glfw(width, height, title):
    if not glfw.init():
        exit(0)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        exit(0)

    glfw.make_context_current(window)
    return window


def bind_vertices(vertices, attributes):
    vertices = (GLfloat * len(vertices))(*vertices)
    array_id = glGenVertexArrays(1)
    glBindVertexArray(array_id)
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)

    vertex_size = sum(attributes)
    offset = 0

    for i, attribute in enumerate(attributes):
        glVertexAttribPointer(i, attribute, GL_FLOAT, GL_FALSE, vertex_size * sizeof(GLfloat),
                              c_void_p(offset * sizeof(GLfloat)))
        glEnableVertexAttribArray(i)
        offset += attribute

    glBindVertexArray(array_id)
    return array_id


def build_shader(shader_name):
    try:
        return compileProgram(
            compileShader(read_shader_file(f"{shader_name}.vs"), GL_VERTEX_SHADER),
            compileShader(read_shader_file(f"{shader_name}.fs"), GL_FRAGMENT_SHADER)
        )
    except RuntimeError as e:
        print(str(e.args[0]).replace("b\"", "\n").replace("\\n", "\n"))
        exit(0)


def resize(w, h, shader_program):
    global width, height
    width = w
    height = h
    if min(width, height) > 0:
        glViewport(0, 0, width, height)
        glUniform1f(glGetUniformLocation(shader_program, "ratio"), width / height)


class Point:
    def __init__(self, pos: Tuple[float, float], color: Tuple[float, float, float, float]):
        self.pos = pos
        self.color = color


def update_buffer(buffer, data):
    glBindBuffer(GL_UNIFORM_BUFFER, buffer)
    glBufferData(GL_UNIFORM_BUFFER, data.size * sizeof(GLfloat), data, GL_DYNAMIC_DRAW)


def get_pos_data(points):
    return numpy.array([x for point in points for x in point.pos + (0, 0)], dtype='float32')


def get_color_data(points):
    return numpy.array([x for point in points for x in point.color], dtype='float32')


def main():
    window = init_glfw(width, height, "Voronoi")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    vertices = bind_vertices([-1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1], (2,))

    points = [
        Point((-0.6, -0.3), (1, 0, 0, 1)),
        Point((0, 0.5), (0, 1, 0, 1)),
        Point((0.5, 0), (0, 0, 1, 1)),
        Point((0, 0), (1, 1, 0, 1)),
        Point((-0.3, 0.6), (1, 0, 1, 1)),
        Point((0.1, -0.6), (0, 1, 1, 1)),
    ]

    shader_program = build_shader("voronoi")

    glUseProgram(shader_program)

    pos_buffer = glGenBuffers(1)
    color_buffer = glGenBuffers(1)
    points_cnt_loc = glGetUniformLocation(shader_program, "pointsCnt")

    update_points(points, pos_buffer, color_buffer, points_cnt_loc)

    current_color = (random.random(), random.random(), random.random(), 1)
    current_color_loc = glGetUniformLocation(shader_program, "currentColor")
    glUniform4f(current_color_loc, *current_color)

    current_point = None
    current_point_loc = glGetUniformLocation(shader_program, "currentPoint")

    def set_current_point(window, x, y):
        nonlocal current_point
        # 2. Сохранить координаты текущей точки в current_point и отправить в шейдер

    def add_point(window, button, action, mods):
        if action != glfw.PRESS:
            return
        nonlocal current_color
        # 3. Добавить текущую точку в список points, обновить буферы и обновить цвет в current_color


    glfw.set_mouse_button_callback(window, add_point)
    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))
    glfw.set_cursor_pos_callback(window, set_current_point)
    resize(width, height, shader_program)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(vertices)
        glBindBufferBase(GL_UNIFORM_BUFFER, 1, pos_buffer)
        glBindBufferBase(GL_UNIFORM_BUFFER, 2, color_buffer)

        glDrawArrays(GL_TRIANGLES, 0, 6)

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


def update_points(points, pos_buffer, color_buffer, points_cnt_loc):
    update_buffer(pos_buffer, get_pos_data(points))
    update_buffer(color_buffer, get_color_data(points))
    glUniform1i(points_cnt_loc, len(points))


if __name__ == "__main__":
    main()
