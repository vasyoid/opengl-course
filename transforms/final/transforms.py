import time
from ctypes import sizeof, c_void_p

import glfw
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def read_shader_file(filename):
    with open(filename) as file:
        return "".join(file.readlines())


def init_glfw(width, height, title):
    if not glfw.init():
        exit(0)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
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
    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)

    vertex_size = sum(attributes)
    offset = 0

    for i, attribute in enumerate(attributes):
        glVertexAttribPointer(i, attribute, GL_FLOAT, GL_FALSE, vertex_size * sizeof(GLfloat), c_void_p(offset * sizeof(GLfloat)))
        glEnableVertexAttribArray(i)
        offset += attribute


def build_shader(shader_name):
    try:
        return compileProgram(
            compileShader(read_shader_file(f"{shader_name}.vs"), GL_VERTEX_SHADER),
            compileShader(read_shader_file(f"{shader_name}.fs"), GL_FRAGMENT_SHADER)
        )
    except RuntimeError as e:
        print(str(e.args[0]).replace("b\"", "\n").replace("\\n", "\n"))
        exit(0)


def load_matrix_to_shader(shader_program, matrix, matrix_name):
    location = glGetUniformLocation(shader_program, matrix_name)
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))


def resize(width, height, shader_program):
    if min(width, height) > 0:
        projection = glm.perspective(glm.radians(45), width / height, 0.1, 100)
        load_matrix_to_shader(shader_program, projection, "projection")
        glViewport(0, 0, width, height)


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "3D")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    vertices = [
        -1, -1, 1, 0, 0, 1,
        1, -1, 1, 0, 0, 1,
        1, 1, 1, 0, 0, 1,
        1, 1, 1, 0, 0, 1,
        -1, 1, 1, 0, 0, 1,
        -1, -1, 1, 0, 0, 1,

        -1, -1, -1, 1, 0, 0,
        -1, 1, -1, 1, 0, 0,
        -1, 1, 1, 1, 0, 0,
        -1, 1, 1, 1, 0, 0,
        -1, -1, 1, 1, 0, 0,
        -1, -1, -1, 1, 0, 0,

        1, -1, -1, 1, 0, 0,
        1, 1, -1, 1, 0, 0,
        1, 1, 1, 1, 0, 0,
        1, 1, 1, 1, 0, 0,
        1, -1, 1, 1, 0, 0,
        1, -1, -1, 1, 0, 0,

        -1, 1, -1, 0, 1, 0,
        1, 1, -1, 0, 1, 0,
        1, 1, 1, 0, 1, 0,
        1, 1, 1, 0, 1, 0,
        -1, 1, 1, 0, 1, 0,
        -1, 1, -1, 0, 1, 0,

        -1, -1, -1, 0, 1, 0,
        1, -1, -1, 0, 1, 0,
        1, -1, 1, 0, 1, 0,
        1, -1, 1, 0, 1, 0,
        -1, -1, 1, 0, 1, 0,
        -1, -1, -1, 0, 1, 0,

        -1, -1, -1, 0, 0, 1,
        1, -1, -1, 0, 0, 1,
        1, 1, -1, 0, 0, 1,
        1, 1, -1, 0, 0, 1,
        -1, 1, -1, 0, 0, 1,
        -1, -1, -1, 0, 0, 1,
    ]

    bind_vertices(vertices, (3, 3))

    shader_program = build_shader("transforms")

    glUseProgram(shader_program)

    view = glm.lookAt((5, 5, 5), (0, 0, 0), (0, 1, 0))
    # view = glm.lookAt((10, 5, 0), (0, 0, 0), (0, 1, 0))

    load_matrix_to_shader(shader_program, view, "view")

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))

    resize(width, height, shader_program)

    task = 0

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)
        if glfw.get_key(window, glfw.KEY_0):
            task = 0
        if glfw.get_key(window, glfw.KEY_1):
            task = 1
        if glfw.get_key(window, glfw.KEY_2):
            task = 2
        if glfw.get_key(window, glfw.KEY_3):
            task = 3
        if glfw.get_key(window, glfw.KEY_4):
            task = 4

        model = glm.mat4(1)

        if task == 0:
            model = glm.rotate(glfw.get_time(), (0, 1, 0))
        elif task == 1:
            model = glm.translate((3, 0, 0)) * glm.rotate(glfw.get_time(), (0, 1, 0))

        elif task == 2:
            model = glm.rotate(glfw.get_time(), (0, 1, 0)) * glm.translate((3, 0, 0))

        elif task == 3:
            model = glm.rotate(glfw.get_time(), (0, 1, 0)) * glm.translate((3, 0, 0)) * glm.rotate(-2 * glfw.get_time(), (0, 1, 0))

        elif task == 4:
            model = glm.rotate(glfw.get_time(), (0, 1, 0)) * glm.translate((3, 0, 0)) * glm.rotate(-2 * glfw.get_time(), (0, 1, 0)) * glm.translate((0, 2 * glm.sin(glfw.get_time() * 3), 0))

        load_matrix_to_shader(shader_program, model, "model")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
