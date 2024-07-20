import time
from ctypes import sizeof, c_void_p

import glfw
import glm
import numpy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image, ImageOps


class Camera:

    def __init__(self, pos=glm.vec3(0, 0, 0), pitch=0, yaw=0):
        self.pos = pos
        self.yaw = yaw
        self.pitch = pitch
        self.world_up = glm.vec3(0, 1, 0)
        self.turn_speed = 0.8
        self.move_speed = 10

    def get_front(self):
        return glm.vec3(
            glm.cos(self.yaw) * glm.cos(self.pitch),
            glm.sin(self.pitch),
            -glm.sin(self.yaw) * glm.cos(self.pitch),
        )

    def get_right(self):
        return glm.normalize(glm.cross(self.get_front(), self.world_up))

    def get_up(self):
        return glm.cross(self.get_right(), self.get_front())

    def get_matrix(self):
        front = self.get_front()
        return glm.lookAt(self.pos, self.pos + front, self.world_up)

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
        self.pos += self.get_up() * delta_time * self.move_speed

    def move_down(self, delta_time):
        self.pos -= self.get_up() * delta_time * self.move_speed


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


class Mesh:
    def __init__(self, vertices, indices, attributes):
        self.vertices = vertices
        self.indices = indices
        self.attributes = attributes
        self.vertex_array_id = None

    def bind_attributes(self):
        vertices = (GLfloat * len(self.vertices))(*self.vertices)
        self.vertex_array_id = glGenVertexArrays(1)
        glBindVertexArray(self.vertex_array_id)
        glBindBuffer(GL_ARRAY_BUFFER, glGenBuffers(1))
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * sizeof(GLfloat), vertices, GL_STATIC_DRAW)

        vertex_size = sum(self.attributes)
        offset = 0

        for i, attribute in enumerate(self.attributes):
            glVertexAttribPointer(i, attribute, GL_FLOAT, GL_FALSE, vertex_size * sizeof(GLfloat),
                                  c_void_p(offset * sizeof(GLfloat)))
            glEnableVertexAttribArray(i)
            offset += attribute

    def draw(self):
        glBindVertexArray(self.vertex_array_id)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices)


def load_mesh(filename):
    vertices = []
    indices = []

    with open(filename) as file:
        for line in file.readlines():
            tokens = line.split()
            if len(tokens) == 0:
                continue
            # TASK1: read mesh data

    return Mesh(vertices, indices, (3, 3, 2))


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "Obj files")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    mesh = load_mesh("../cottage.obj")
    mesh.bind_attributes()
    # TASK2: load texture from "../cottage.png"

    shader_program = build_shader("obj_files")

    glUseProgram(shader_program)

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))

    resize(width, height, shader_program)

    camera = Camera(pos=glm.vec3(-40, 25, -20), pitch=-0.5, yaw=-0.5)

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

        light_pos = (150 * glm.cos(glfw.get_time()), 50, 150 * glm.sin(glfw.get_time()))
        light_pos_location = glGetUniformLocation(shader_program, "lightPos")
        glUniform3f(light_pos_location, *light_pos)

        view_pos = camera.pos
        view_pos_location = glGetUniformLocation(shader_program, "viewPos")
        glUniform3f(view_pos_location, *view_pos)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = glm.mat4()
        load_matrix_to_shader(shader_program, model, "model")
        # TASK2: bind texture
        mesh.draw()

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
