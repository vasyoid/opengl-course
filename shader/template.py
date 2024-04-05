from math import sqrt
from ctypes import sizeof, c_void_p

import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Vertex Shader
VERTEX_SHADER = """
#version 330

in vec3 vPos;
in vec3 vColor;

out vec3 color;
out vec3 pos;

void main()
{
    gl_Position = vec4(vPos, 1.0);
    pos = vPos;
    color = vColor;
}
"""

# Fragment Shader
FRAGMENT_SHADER = """
#version 330

in vec3 pos;
in vec3 color;
out vec4 fragColor;

void main()
{
    fragColor = vec4(color, 1.0);
}
"""


def main():
    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Compile shaders and program
    shader_program = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    # Vertex data
    vertices = [
        -0.5 * sqrt(3), -1 / 2, 0, 1, 1, 1,
        0.5 * sqrt(3), -1 / 2, 0, 1, 1, 1,
        0, 1, 0, 1, 1, 1
    ]

    bind_vertices(shader_program, vertices)

    # Use the shader program
    glUseProgram(shader_program)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


def bind_vertices(shader_program, vertices):
    # Convert vertex data to a format OpenGL understands
    vertices = (GLfloat * len(vertices))(*vertices)
    # Bind the Vertex Array Object
    glBindVertexArray(glGenVertexArrays(1))
    # Bind the buffer and upload data
    glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)
    # Enable vertex pos attribute
    v_pos = glGetAttribLocation(shader_program, "vPos")
    glVertexAttribPointer(v_pos, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), c_void_p(0))
    glEnableVertexAttribArray(v_pos)
    # Enable vertex color attribute
    v_color = glGetAttribLocation(shader_program, "vColor")
    glVertexAttribPointer(v_color, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(GLfloat), c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(v_color)


if __name__ == "__main__":
    main()
