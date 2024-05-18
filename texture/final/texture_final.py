import time
from ctypes import sizeof, c_void_p

import glfw
import glm
import numpy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image


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


def load_matrix_to_shader(shader_program, matrix, matrix_name):
    location = glGetUniformLocation(shader_program, matrix_name)
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))


def resize(width, height, shader_program):
    if min(width, height) > 0:
        projection = glm.perspective(glm.radians(45), width / height, 0.1, 100)
        load_matrix_to_shader(shader_program, projection, "projection")
        glViewport(0, 0, width, height)


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


def build_cube_1():
    return [
        -1, -1, 1, 0, 1,
        1, -1, 1, 1, 1,
        1, 1, 1, 1, 0,
        1, 1, 1, 1, 0,
        -1, 1, 1, 0, 0,
        -1, -1, 1, 0, 1,

        1, -1, -1, 1, 1,
        1, 1, -1, 1, 0,
        1, 1, 1, 0, 0,
        1, 1, 1, 0, 0,
        1, -1, 1, 0, 1,
        1, -1, -1, 1, 1,

        -1, -1, -1, 1, 1,
        1, -1, -1, 0, 1,
        1, 1, -1, 0, 0,
        1, 1, -1, 0, 0,
        -1, 1, -1, 1, 0,
        -1, -1, -1, 1, 1,

        -1, -1, -1, 0, 1,
        -1, 1, -1, 0, 0,
        -1, 1, 1, 1, 0,
        -1, 1, 1, 1, 0,
        -1, -1, 1, 1, 1,
        -1, -1, -1, 0, 1,

        -1, 1, -1, 0, 1,
        1, 1, -1, 0, 0,
        1, 1, 1, 1, 0,
        1, 1, 1, 1, 0,
        -1, 1, 1, 1, 1,
        -1, 1, -1, 0, 1,

        -1, -1, -1, 0, 1,
        1, -1, -1, 1, 1,
        1, -1, 1, 1, 0,
        1, -1, 1, 1, 0,
        -1, -1, 1, 0, 0,
        -1, -1, -1, 0, 1,
    ]


def build_cube_2():
    return [
        -1, -1, 1, 0, 2,
        1, -1, 1, 2, 2,
        1, 1, 1, 2, 0,
        1, 1, 1, 2, 0,
        -1, 1, 1, 0, 0,
        -1, -1, 1, 0, 2,

        1, -1, -1, 2, 2,
        1, 1, -1, 2, 0,
        1, 1, 1, 0, 0,
        1, 1, 1, 0, 0,
        1, -1, 1, 0, 2,
        1, -1, -1, 2, 2,

        -1, -1, -1, 2, 2,
        1, -1, -1, 0, 2,
        1, 1, -1, 0, 0,
        1, 1, -1, 0, 0,
        -1, 1, -1, 2, 0,
        -1, -1, -1, 2, 2,

        -1, -1, -1, 0, 2,
        -1, 1, -1, 0, 0,
        -1, 1, 1, 2, 0,
        -1, 1, 1, 2, 0,
        -1, -1, 1, 2, 2,
        -1, -1, -1, 0, 2,

        -1, 1, -1, 0, 2,
        1, 1, -1, 0, 0,
        1, 1, 1, 2, 0,
        1, 1, 1, 2, 0,
        -1, 1, 1, 2, 2,
        -1, 1, -1, 0, 2,

        -1, -1, -1, 0, 2,
        1, -1, -1, 2, 2,
        1, -1, 1, 2, 0,
        1, -1, 1, 2, 0,
        -1, -1, 1, 0, 0,
        -1, -1, -1, 0, 2,
    ]


def build_cube_3():
    return [
        -1, -1, 1, 0 / 4, 2 / 4,
        1, -1, 1, 1 / 4, 2 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        -1, 1, 1, 0 / 4, 1 / 4,
        -1, -1, 1, 0 / 4, 2 / 4,

        1, -1, -1, 2 / 4, 2 / 4,
        1, 1, -1, 2 / 4, 1 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        1, -1, 1, 1 / 4, 2 / 4,
        1, -1, -1, 2 / 4, 2 / 4,

        -1, -1, -1, 3 / 4, 2 / 4,
        1, -1, -1, 2 / 4, 2 / 4,
        1, 1, -1, 2 / 4, 1 / 4,
        1, 1, -1, 2 / 4, 1 / 4,
        -1, 1, -1, 3 / 4, 1 / 4,
        -1, -1, -1, 3 / 4, 2 / 4,

        -1, -1, -1, 3 / 4, 2 / 4,
        -1, 1, -1, 3 / 4, 1 / 4,
        -1, 1, 1, 4 / 4, 1 / 4,
        -1, 1, 1, 4 / 4, 1 / 4,
        -1, -1, 1, 4 / 4, 2 / 4,
        -1, -1, -1, 3 / 4, 2 / 4,

        -1, 1, -1, 2 / 4, 0 / 4,
        1, 1, -1, 2 / 4, 1 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        1, 1, 1, 1 / 4, 1 / 4,
        -1, 1, 1, 1 / 4, 0 / 4,
        -1, 1, -1, 2 / 4, 0 / 4,

        -1, -1, -1, 2 / 4, 3 / 4,
        1, -1, -1, 2 / 4, 2 / 4,
        1, -1, 1, 1 / 4, 2 / 4,
        1, -1, 1, 1 / 4, 2 / 4,
        -1, -1, 1, 1 / 4, 3 / 4,
        -1, -1, -1, 2 / 4, 3 / 4,
    ]


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "Texture")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    cube_1 = bind_vertices(build_cube_1(), (3, 2))
    cube_2 = bind_vertices(build_cube_2(), (3, 2))
    cube_3 = bind_vertices(build_cube_3(), (3, 2))

    shader_program = build_shader("texture")

    glUseProgram(shader_program)

    tex_wood = load_texture("../../camera/wood.png")
    tex_gold = load_texture("../gold.png")
    tex_lake = load_texture("../lake.png")
    tex_world = load_texture("../canyon.jpg")

    camera_pos = [0, 0, 10]

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))

    resize(width, height, shader_program)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            camera_pos[1] += 1
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            camera_pos[1] -= 1

        view = glm.lookAt(camera_pos, (0, 0, 0), (0, 1, 0))
        load_matrix_to_shader(shader_program, view, "view")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = glm.translate((-2, 2, 0)) * glm.rotate(glfw.get_time() / 5, (0, 1, 0))
        glBindVertexArray(cube_1)
        glBindTexture(GL_TEXTURE_2D, tex_wood)
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, 36)

        model = glm.translate((2, 2, 0)) * glm.rotate(glfw.get_time() / 5, (0, 1, 0))
        glBindVertexArray(cube_1)
        glBindTexture(GL_TEXTURE_2D, tex_gold)
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, 36)

        model = glm.translate((-2, -2, 0)) * glm.rotate(glfw.get_time() / 5, (0, 1, 0))
        glBindVertexArray(cube_2)
        glBindTexture(GL_TEXTURE_2D, tex_lake)
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, 36)

        model = glm.translate((2, -2, 0)) * glm.rotate(glfw.get_time() / 5, (0, 1, 0))
        glBindVertexArray(cube_3)
        glBindTexture(GL_TEXTURE_2D, tex_world)
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
