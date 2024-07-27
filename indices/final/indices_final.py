import time
from ctypes import sizeof, c_void_p

import glfw
import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class Camera:

    def __init__(self, pos=glm.vec3(0, 0, 0), pitch=0, yaw=0):
        self.pos = pos
        self.yaw = yaw
        self.pitch = pitch
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


def build_cube():
    vertices = [
        1, -1, 1, 0, 0, 1,
        1, 1, 1, 0, 0, 1,
        -1, 1, 1, 0, 0, 1,
        -1, -1, 1, 0, 0, 1,

        1, 1, -1, 1, 0, 0,
        1, 1, 1, 1, 0, 0,
        1, -1, 1, 1, 0, 0,
        1, -1, -1, 1, 0, 0,

        1, -1, -1, 0, 0, -1,
        1, 1, -1, 0, 0, -1,
        -1, 1, -1, 0, 0, -1,
        -1, -1, -1, 0, 0, -1,

        -1, 1, -1, -1, 0, 0,
        -1, 1, 1, -1, 0, 0,
        -1, -1, 1, -1, 0, 0,
        -1, -1, -1, -1, 0, 0,

        1, 1, -1, 0, 1, 0,
        1, 1, 1, 0, 1, 0,
        -1, 1, 1, 0, 1, 0,
        -1, 1, -1, 0, 1, 0,

        1, -1, -1, 0, -1, 0,
        1, -1, 1, 0, -1, 0,
        -1, -1, 1, 0, -1, 0,
        -1, -1, -1, 0, -1, 0,
    ]
    indices = [
        0, 1, 2, 0, 2, 3,
        4, 5, 6, 4, 6, 7,
        8, 9, 10, 8, 10, 11,
        12, 13, 14, 12, 14, 15,
        16, 17, 18, 16, 18, 19,
        20, 21, 22, 20, 22, 23
    ]
    return Mesh(vertices, indices, (3, 3))


def build_cylinder(h_div, h, r):
    vertices = []
    for y in (-h / 2, h / 2):
        for i in range(h_div):
            phi = 2 * glm.pi() / h_div * i
            vertices.extend((glm.cos(phi) * r, y, glm.sin(phi) * r))
            vertices.extend((glm.cos(phi) * r, 0, glm.sin(phi) * r))

    for y in (-1, 1):
        for i in range(h_div):
            phi = 2 * glm.pi() / h_div * i
            vertices.extend((glm.cos(phi) * r, h / 2 * y, glm.sin(phi) * r))
            vertices.extend((0, y, 0))

    for y in (-1, 1):
        vertices.extend((0, h / 2 * y, 0))
        vertices.extend((0, y, 0))

    indices = []

    for j in range(h_div):
        # side
        indices.append(j)
        indices.append((j + 1) % h_div)
        indices.append(h_div + j)
        indices.append((j + 1) % h_div)
        indices.append(h_div + j)
        indices.append(h_div + (j + 1) % h_div)
        # top
        indices.append(2 * h_div + j)
        indices.append(2 * h_div + (j + 1) % h_div)
        indices.append(4 * h_div)
        # bottom
        indices.append(3 * h_div + j)
        indices.append(3 * h_div + (j + 1) % h_div)
        indices.append(4 * h_div + 1)

    return Mesh(vertices, indices, (3, 3))


def build_cone(h_div, h, r):
    vertices = []
    n = glm.normalize(glm.vec2(h, r))
    for i in range(h_div):
        phi = 2 * glm.pi() / h_div * i
        vertices.extend((glm.cos(phi) * r, -h / 2, glm.sin(phi) * r))
        vertices.extend((glm.cos(phi) * n.x, n.y, glm.sin(phi) * n.x))
    for i in range(h_div):
        phi = 2 * glm.pi() / h_div * i
        vertices.extend((0, h / 2, 0))
        vertices.extend((glm.cos(phi) * n.x, n.y, glm.sin(phi) * n.x))
    for i in range(h_div):
        phi = 2 * glm.pi() / h_div * i
        vertices.extend((glm.cos(phi) * r, -h / 2, glm.sin(phi) * r))
        vertices.extend((0, -1, 0))
    vertices.extend((0, 0, 0))
    vertices.extend((0, -1, 0))

    indices = []

    for j in range(h_div):
        # side
        indices.append(j)
        indices.append((j + 1) % h_div)
        indices.append(h_div + j)
        indices.append((j + 1) % h_div)
        indices.append(h_div + j)
        indices.append(h_div + (j + 1) % h_div)

        # bottom
        indices.append(2 * h_div + j)
        indices.append(2 * h_div + (j + 1) % h_div)
        indices.append(2 * h_div + 1)

    return Mesh(vertices, indices, (3, 3))


def get_point(phi, theta):
    return (
        glm.cos(phi) * glm.cos(theta),
        glm.sin(theta),
        glm.sin(phi) * glm.cos(theta),
    )


def build_sphere(h_div, v_div):
    vertices = []
    for i in range(v_div + 1):
        theta = -glm.pi() / 2 + glm.pi() / v_div * i
        for j in range(h_div):
            phi = 2 * glm.pi() / h_div * j
            vertices.extend(get_point(phi, theta))
            vertices.extend(get_point(phi, theta))

    indices = []

    for i in range(v_div):
        for j in range(h_div):
            indices.append(i * h_div + j)
            indices.append(i * h_div + (j + 1) % h_div)
            indices.append((i + 1) * h_div + j)
            indices.append(i * h_div + (j + 1) % h_div)
            indices.append((i + 1) * h_div + j)
            indices.append((i + 1) * h_div + (j + 1) % h_div)

    return Mesh(vertices, indices, (3, 3))


def main():
    width = 1000
    height = 800

    window = init_glfw(width, height, "Indices")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)

    cube_mesh = build_cube()
    cube_mesh.bind_attributes()

    sphere_mesh = build_sphere(30, 30)
    sphere_mesh.bind_attributes()

    cylinder_mesh = build_cylinder(30, 2, 1)
    cylinder_mesh.bind_attributes()

    cone_mesh = build_cone(100, 2, 1)
    cone_mesh.bind_attributes()

    shader_program = build_shader("indices")

    glUseProgram(shader_program)

    glfw.set_window_size_callback(window, lambda _, w, h: resize(w, h, shader_program))

    resize(width, height, shader_program)

    camera = Camera(pos=glm.vec3(0, 5, 0), pitch=-0.5)

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

        light_pos = (10 * glm.cos(glfw.get_time()), 7, 10 * glm.sin(glfw.get_time()))
        light_pos_location = glGetUniformLocation(shader_program, "lightPos")
        glUniform3f(light_pos_location, *light_pos)

        view_pos = camera.pos
        view_pos_location = glGetUniformLocation(shader_program, "viewPos")
        glUniform3f(view_pos_location, *view_pos)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = glm.translate((10, -3, -2))
        load_matrix_to_shader(shader_program, model, "model")
        cube_mesh.draw()

        model = glm.translate((10, -3, 2))
        load_matrix_to_shader(shader_program, model, "model")
        sphere_mesh.draw()

        model = glm.translate((15, -3, -2))
        load_matrix_to_shader(shader_program, model, "model")
        cylinder_mesh.draw()

        model = glm.translate((15, -3, 2))
        load_matrix_to_shader(shader_program, model, "model")
        load_matrix_to_shader(shader_program, model, "model")
        cone_mesh.draw()

        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
