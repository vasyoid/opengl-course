import time
from ctypes import sizeof, c_void_p

import glfw
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Camera:

    def __init__(self):
        self.pos = glm.vec3(0, 0, 0)
        self.yaw = 0
        self.pitch = 0
        self.world_up = glm.vec3(0, 1, 0)
        self.turn_speed = 0.8
        self.move_speed = 2

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


def build_cube():
    # TASK_2: set correct normal for each vertex
    return [
        -1, -1, 1, 0, 0, 0,
        1, -1, 1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        -1, 1, 1, 0, 0, 0,
        -1, -1, 1, 0, 0, 0,

        1, -1, -1, 0, 0, 0,
        1, 1, -1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        1, -1, 1, 0, 0, 0,
        1, -1, -1, 0, 0, 0,

        -1, -1, -1, 0, 0, 0,
        1, -1, -1, 0, 0, 0,
        1, 1, -1, 0, 0, 0,
        1, 1, -1, 0, 0, 0,
        -1, 1, -1, 0, 0, 0,
        -1, -1, -1, 0, 0, 0,

        -1, -1, -1, 0, 0, 0,
        -1, 1, -1, 0, 0, 0,
        -1, 1, 1, 0, 0, 0,
        -1, 1, 1, 0, 0, 0,
        -1, -1, 1, 0, 0, 0,
        -1, -1, -1, 0, 0, 0,

        -1, 1, -1, 0, 0, 0,
        1, 1, -1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        1, 1, 1, 0, 0, 0,
        -1, 1, 1, 0, 0, 0,
        -1, 1, -1, 0, 0, 0,

        -1, -1, -1, 0, 0, 0,
        1, -1, -1, 0, 0, 0,
        1, -1, 1, 0, 0, 0,
        1, -1, 1, 0, 0, 0,
        -1, -1, 1, 0, 0, 0,
        -1, -1, -1, 0, 0, 0,
    ]


def get_point(phi, theta):
    return (
        glm.cos(phi) * glm.cos(theta),
        glm.sin(theta),
        glm.sin(phi) * glm.cos(theta),
    )


def build_sphere(h_div, v_div):
    # TASK_4: build sphere
    sphere = [
        0, 0, 0, 0, 0, 0,
        0, 0, 1, 0, 0, 0,
        0, 1, 0, 0, 0, 0,
    ]
    return sphere


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "Diffuse")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    cube_vertices = build_cube()
    cube = bind_vertices(cube_vertices, (3, 3))

    sphere_vertices = build_sphere(100, 50)
    sphere = bind_vertices(sphere_vertices, (3, 3))

    shader_program = build_shader("lighting")

    glUseProgram(shader_program)

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

        # TASK_5: change lightPos to make it fly around the scene
        light_pos = (-10, 7, 5)
        light_pos_location = glGetUniformLocation(shader_program, "lightPos")
        glUniform3f(light_pos_location, *light_pos)

        # TASK_3: set shader uniform variable "viewPos" to camera position
        pass

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glBindVertexArray(cube)
        model = glm.translate((10, -3, -2))
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, len(cube_vertices) // 6)

        glBindVertexArray(sphere)
        model = glm.translate((10, -3, 2))
        load_matrix_to_shader(shader_program, model, "model")
        glDrawArrays(GL_TRIANGLES, 0, len(sphere_vertices) // 6)

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
