import time
from ctypes import sizeof, c_void_p

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def read_shader_file(filename):
    with open(filename) as file:
        return "".join(file.readlines())


def init_glfw():
    if not glfw.init():
        exit(0)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(800, 800, "Fractal", None, None)

    if not window:
        glfw.terminate()
        exit(0)

    glfw.make_context_current(window)
    return window


def bind_vertices(vertices):
    vertices = (GLfloat * len(vertices))(*vertices)
    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
    glEnableVertexAttribArray(0)


def main():
    window = init_glfw()

    vertices = [
        -1, -1, 0,
        1, -1, 0,
        1, 1, 0,

        1, 1, 0,
        -1, 1, 0,
        -1, -1, 0
    ]

    shader_program = compileProgram(
        compileShader(read_shader_file("fractal.vs"), GL_VERTEX_SHADER),
        compileShader(read_shader_file("fractal.fs"), GL_FRAGMENT_SHADER)
    )

    bind_vertices(vertices)
    glUseProgram(shader_program)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)


        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
