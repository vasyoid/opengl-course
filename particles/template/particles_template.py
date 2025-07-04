import math
import random
import time
from ctypes import sizeof, c_void_p

import glfw
import numpy
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image

width = 800
height = 800
PARTICLES_NUM = 2000


def read_shader_file(filename):
    with open(filename) as file:
        return "".join(file.readlines())


def load_texture(filepath):
    img = Image.open(filepath).convert("RGBA")
    img_data = numpy.array(list(img.getdata()), numpy.uint8)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


def init_glfw(width, height, title):
    if not glfw.init():
        exit(0)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        exit(0)

    glfw.make_context_current(window)
    return window


def build_shader(shader_name):
    try:
        return compileProgram(
            compileShader(read_shader_file(f"{shader_name}.vs"), GL_VERTEX_SHADER),
            compileShader(read_shader_file(f"{shader_name}.fs"), GL_FRAGMENT_SHADER)
        )
    except RuntimeError as e:
        print(str(e.args[0]).replace("b\"", "\n").replace("\\n", "\n"))
        exit(0)


def resize(w, h):
    global width, height
    width = w
    height = h
    if min(width, height) > 0:
        glViewport(0, 0, width, height)


class Particle:
    def __init__(self, ttl):
        self.pos = (0, 0)
        self.v = (0, 0)
        self.color = (0, 0, 0, 0)
        self.ttl = ttl
        self.size = 0


def get_pos_and_size_data(particles):
    return numpy.array([x for p in particles for x in p.pos + (p.size,)], dtype='float32')


def get_color_data(particles):
    return numpy.array([x for p in particles for x in p.color], dtype='float32')


def float_array(data):
    return np.array(data, dtype=np.float32)


def init_buffers(vertex_buffer, pos_buffer, color_buffer):
    vertices = [
        -1, -1,
        1, -1,
        1, 1,
        1, 1,
        -1, 1,
        -1, -1
    ]

    glBindVertexArray(glGenVertexArrays(1))
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), float_array(vertices), GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, pos_buffer)
    glBufferData(GL_ARRAY_BUFFER, PARTICLES_NUM * 4 * sizeof(GLfloat), None, GL_STREAM_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))

    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
    glBufferData(GL_ARRAY_BUFFER, PARTICLES_NUM * 4 * sizeof(GLfloat), None, GL_STREAM_DRAW)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), c_void_p(0))

    glVertexAttribDivisor(0, 0)
    glVertexAttribDivisor(1, 1)
    glVertexAttribDivisor(2, 1)


def main():
    window = init_glfw(width, height, "Particles")
    print(glGetString(GL_VERSION))
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    particles = [Particle(i / PARTICLES_NUM * 4) for i in range(PARTICLES_NUM)]

    shader_program = build_shader("particles")
    glUseProgram(shader_program)

    vertex_buffer = glGenBuffers(1)
    pos_buffer = glGenBuffers(1)
    color_buffer = glGenBuffers(1)
    init_buffers(vertex_buffer, pos_buffer, color_buffer)

    tex = load_texture("../texture/particle.png")
    glBindTexture(GL_TEXTURE_2D, tex)

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h))
    resize(width, height)

    prev_time = time.time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        cur_time = time.time()
        delta_time = cur_time - prev_time
        prev_time = cur_time

        for particle in particles:
            if particle.ttl <= 0:
                ...  # 3. Setup new particle parameters
            else:
                ...  # 3. Update particle

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindBuffer(GL_ARRAY_BUFFER, pos_buffer)
        glBufferData(GL_ARRAY_BUFFER, len(particles) * 3 * sizeof(GLfloat), get_pos_and_size_data(particles), GL_STREAM_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
        glBufferData(GL_ARRAY_BUFFER, len(particles) * 4 * sizeof(GLfloat), get_color_data(particles), GL_STREAM_DRAW)

        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, len(particles))
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
