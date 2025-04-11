import time
from ctypes import sizeof, c_void_p

import glfw
import glm
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

    window = glfw.create_window(800, 800, "Ray marching", None, None)

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


# def resize(width, height, shader_program):
#     if min(width, height) > 0:
#         projection = glm.perspective(glm.radians(45), width / height, 0.1, 100)
#         load_matrix_to_shader(shader_program, projection, "projection")
#         glViewport(0, 0, width, height)


def load_matrix_to_shader(shader_program, matrix, matrix_name):
    location = glGetUniformLocation(shader_program, matrix_name)
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))


def load_uniform_to_shader(shader_program, uniform_value, uniform_name, component_count):
    location = glGetUniformLocation(shader_program, uniform_name)
    if component_count == 1:
        glUniform1f(location, uniform_value)
    elif component_count == 2:
        glUniform2f(location, *uniform_value)
    elif component_count == 3:
        glUniform3f(location, *uniform_value)
    else:
        raise ValueError(f"Unsupported component count: {component_count}")


class Camera:
    def __init__(self):
        self.pos = glm.vec3(0, 0, 0)
        self.yaw = 0
        self.pitch = 0
        self.world_up = glm.vec3(0, 1, 0)
        self.turn_speed = 0.8
        self.move_speed = 1

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


def main():
    window = init_glfw()

    vertices = [
        -1, -1, -1,
        1, -1, -1,
        1, 1, -1,

        1, 1, -1,
        -1, 1, -1,
        -1, -1, -1
    ]

    shader_program = compileProgram(
        compileShader(read_shader_file("ray_marching.vs"), GL_VERTEX_SHADER),
        compileShader(read_shader_file("ray_marching.fs"), GL_FRAGMENT_SHADER)
    )

    bind_vertices(vertices)
    glUseProgram(shader_program)

    camera = Camera()

    sphere_pos = glm.vec3(3, 0, -1)
    cube_pos = glm.vec3(3, 0, 1)
    cylinder_pos = glm.vec3(3, 0, 0)

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
        if glfw.get_key(window, glfw.KEY_I) == glfw.PRESS:
            print(glm.inverse(camera.get_matrix()) * glm.vec4(0, 0, -1, 1))
            print(camera.get_front())

        view = camera.get_matrix()
        load_matrix_to_shader(shader_program, glm.inverse(view), "view_inv")
        load_uniform_to_shader(shader_program, camera.pos, "u_cam_pos", 3)
        load_uniform_to_shader(shader_program, sphere_pos, "u_sphere_pos", 3)
        load_uniform_to_shader(shader_program, cube_pos, "u_cube_pos", 3)
        load_uniform_to_shader(shader_program, cylinder_pos, "u_cylinder_pos", 3)

        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
