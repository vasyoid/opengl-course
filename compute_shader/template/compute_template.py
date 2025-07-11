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


def build_comp_shader(shader_name):
    try:
        return compileProgram(compileShader(read_shader_file(f"{shader_name}.comp"), GL_COMPUTE_SHADER))
    except RuntimeError as e:
        print(str(e.args[0]).replace("b\"", "\n").replace("\\n", "\n"))
        exit(0)


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

def get_pos_and_size_data(particles):
    return numpy.array([x for p in particles for x in p.pos + (p.size, p.ttl)], dtype='float32')


def get_color_data(particles):
    return numpy.array([x for p in particles for x in p.color], dtype='float32')


def main():
    PARTICLES_NUM = 200000

    window = init_glfw(width, height, "Particles")

    print(glGetString(GL_VERSION))

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertices = [
        -1, -1,
        1, -1,
        1, 1,
        1, 1,
        -1, 1,
        -1, -1
    ]

    glBindVertexArray(glGenVertexArrays(1))
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)

    color_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
    glBufferData(GL_ARRAY_BUFFER, PARTICLES_NUM * 4 * sizeof(GLfloat),
                 np.array([random.random() for _ in range(4 * PARTICLES_NUM)], dtype=numpy.float32), GL_STATIC_DRAW)

    pos_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, pos_buffer)
    glBufferData(GL_ARRAY_BUFFER, PARTICLES_NUM * 4 * sizeof(GLfloat),
                 np.array([0 for _ in range(4 * PARTICLES_NUM)], dtype=numpy.float32), GL_STREAM_DRAW)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, pos_buffer)

    params_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, params_buffer)
    glBufferData(GL_ARRAY_BUFFER, PARTICLES_NUM * 4 * sizeof(GLfloat),
                 np.array([j for i in range(PARTICLES_NUM) for j in (0, 0, i / PARTICLES_NUM * 4, 0)], dtype=numpy.float32), GL_STREAM_DRAW)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, params_buffer)

    shader_program = build_shader("particles")
    compute_program = build_comp_shader("particles")

    delta_time_loc = glGetUniformLocation(compute_program, "deltaTime")
    time_loc = glGetUniformLocation(compute_program, "time")

    tex = load_texture("../texture/particle.png")

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h))
    resize(width, height)

    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), c_void_p(0))

    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, pos_buffer)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), c_void_p(0))

    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 4 * sizeof(GLfloat), c_void_p(0))

    glVertexAttribDivisor(0, 0)
    glVertexAttribDivisor(1, 1)
    glVertexAttribDivisor(2, 1)

    glBindTexture(GL_TEXTURE_2D, tex)

    prev_time = time.time()
    n = 0
    while not glfw.window_should_close(window):
        cur_time = time.time()
        delta_time = cur_time - prev_time
        prev_time = cur_time

        glfw.poll_events()

        glUseProgram(compute_program)
        glUniform1f(delta_time_loc, delta_time)
        glUniform1f(time_loc, cur_time)
        glDispatchCompute((PARTICLES_NUM + 255) // 256, 1, 1)
        glMemoryBarrier(GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)

        glUseProgram(shader_program)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, PARTICLES_NUM)
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
