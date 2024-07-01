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
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


def build_cube():
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


class Camera:

    def __init__(self):
        self.pos = glm.vec3(0, 0, 0)
        self.yaw = 0
        self.pitch = 0
        self.up = glm.vec3(0, 1, 0)
        self.turn_speed = 0.8
        self.move_speed = 2

    def get_front(self):
        return glm.vec3(
            glm.cos(self.yaw) * glm.cos(self.pitch),
            glm.sin(self.pitch),
            glm.sin(self.yaw) * glm.cos(self.pitch),
        )

    def get_right(self):
        return glm.normalize(glm.cross(self.get_front(), self.up))

    def get_matrix(self):
        front = self.get_front()
        return glm.lookAt(self.pos, self.pos + front, self.up)

    def turn_left(self, delta_time):
        self.yaw += delta_time * self.turn_speed

    def turn_right(self, delta_time):
        self.yaw -= delta_time * self.turn_speed

    def turn_up(self, delta_time):
        self.pitch += delta_time * self.turn_speed

    def turn_down(self, delta_time):
        self.pitch -= delta_time * self.turn_speed

    def move_left(self, delta_time):
        self.pos -= self.get_right() * delta_time * self.move_speed

    def move_right(self, delta_time):
        self.pos += self.get_right() * delta_time * self.move_speed

    def move_forward(self, delta_time):
        self.pos += self.get_front() * delta_time * self.move_speed

    def move_backward(self, delta_time):
        self.pos -= self.get_front() * delta_time * self.move_speed

    def move_up(self, delta_time):
        self.pos += self.up * delta_time * self.move_speed

    def move_down(self, delta_time):
        self.pos -= self.up * delta_time * self.move_speed


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "Camera")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    cube = bind_vertices(build_cube(), (3, 2))

    shader_program = build_shader("camera")

    glUseProgram(shader_program)

    texture = load_texture("../wood.png")

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))

    resize(width, height, shader_program)

    camera = Camera()

    prev_time = glfw.get_time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        cur_time = glfw.get_time()
        delta_time = cur_time - prev_time
        prev_time = cur_time

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            camera.turn_left(delta_time)
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            camera.turn_right(delta_time)
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            camera.turn_up(delta_time)
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            camera.turn_down(delta_time)
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camera.move_left(delta_time)
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            camera.move_right(delta_time)
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camera.move_forward(delta_time)
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camera.move_backward(delta_time)
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            camera.move_up(delta_time)
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            camera.move_down(delta_time)

        view = camera.get_matrix()
        load_matrix_to_shader(shader_program, view, "view")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(cube)
        glBindTexture(GL_TEXTURE_2D, texture)

        for i in range(12):
            model = glm.rotate(glm.radians(360 / 12 * i), (0, 1, 0)) * glm.translate((10, 0, 0)) * glm.rotate(
                glfw.get_time() / 5, (0, 1, 0))
            load_matrix_to_shader(shader_program, model, "model")
            glDrawArrays(GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
