import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from ctypes import c_void_p, sizeof
from math import sqrt

# Define your shaders here
VERTEX_SHADER = """
#version 330

layout (location = 0) in vec3 vPos;
layout (location = 1) in vec3 vColor;
out vec3 color;

void main() {
    gl_Position = vec4(vPos, 1.0);
    color = vColor;
}
"""

FRAGMENT_SHADER = """
#version 330

in vec3 color;
out vec4 outColor;

void main() {
    outColor = vec4(color, 1.0);
}
"""

def bind_vertices( vertices):
    vertices = (GLfloat * len(vertices))(*vertices)
    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)
    # v_pos = glGetAttribLocation(shader_program, "vPos")
    v_pos = 0
    glVertexAttribPointer(v_pos, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), c_void_p(0))
    glEnableVertexAttribArray(v_pos)
    # v_color = glGetAttribLocation(shader_program, "vColor")
    v_color = 1
    glVertexAttribPointer(v_color, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(v_color)

def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(800, 800, "GLFW Window", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glClearColor(0.1, 0.1, 0.12, 1)

    vertices = [
        -0.5 * sqrt(3), -1 / 2, 0, 1, 0, 0,
        0.5 * sqrt(3), -1 / 2, 0, 0, 1, 0,
        0, 1, 0, 0, 0, 1
    ]

    bind_vertices(vertices)

    shader_program = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    glUseProgram(shader_program)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)

        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()