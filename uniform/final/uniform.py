import time
from ctypes import sizeof, c_void_p

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class MouseController:
    def __init__(self, window):
        self.events = []
        self.is_dragging = False
        self.last_mouse_position = None
        glfw.set_mouse_button_callback(window, lambda _, button, action, __: self.mouse_button_callback(button, action))
        glfw.set_cursor_pos_callback(window, lambda _, x, y: self.cursor_pos_callback(x, y))
        glfw.set_scroll_callback(window, lambda _, __, offset: self.scroll_callback(offset))

    def mouse_button_callback(self, button, action):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.is_dragging = True
            elif action == glfw.RELEASE:
                self.is_dragging = False

    def cursor_pos_callback(self, x, y):
        if self.is_dragging:
            if self.last_mouse_position:
                dx = x - self.last_mouse_position[0]
                dy = y - self.last_mouse_position[1]
                self.events.append({"type": "drag", "dx": dx, "dy": dy})
        self.last_mouse_position = (x, y)

    def scroll_callback(self, offset):
        self.events.append({"type": "scroll", "delta": offset})

    def get_events(self):
        events = self.events.copy()
        self.events.clear()
        return events


def read_shader_file(filename):
    with open(filename) as file:
        return "".join(file.readlines())


def init_glfw(width, height, title):
    if not glfw.init():
        exit(0)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    window = glfw.create_window(width, height, title, None, None)

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


def update_shift_and_zoom(shift_x, shift_y, zoom, shader_program):
    shift_location = glGetUniformLocation(shader_program, "shift")
    glUniform2f(shift_location, shift_x, shift_y)
    zoom_location = glGetUniformLocation(shader_program, "zoom")
    glUniform1f(zoom_location, zoom)


def main():
    width = 800
    height = 800

    shift_x = 0.5
    shift_y = 0
    zoom = 1

    window = init_glfw(width, height, "Fractal")

    vertices = [
        -1, -1, 0,
        1, -1, 0,
        1, 1, 0,

        1, 1, 0,
        -1, 1, 0,
        -1, -1, 0
    ]

    shader_program = compileProgram(
        compileShader(read_shader_file("uniform.vs"), GL_VERTEX_SHADER),
        compileShader(read_shader_file("uniform.fs"), GL_FRAGMENT_SHADER)
    )

    bind_vertices(vertices)
    glUseProgram(shader_program)

    update_shift_and_zoom(shift_x, shift_y, zoom, shader_program)

    mouse_controller = MouseController(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        for event in mouse_controller.get_events():
            if event["type"] == "drag":
                dx, dy = event["dx"], event["dy"]
                shift_x += 2 * dx / width / zoom
                shift_y -= 2 * dy / height / zoom
            elif event["type"] == "scroll":
                x, y = glfw.get_cursor_pos(window)
                delta = event["delta"]
                shift_x -= (2 * x / width - 1) * delta / (zoom * (1 + delta))
                shift_y -= (1 - 2 * y / height) * delta / (zoom * (1 + delta))
                zoom *= (1 + delta)
        update_shift_and_zoom(shift_x, shift_y, zoom, shader_program)

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, glfw.TRUE)

        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glfw.swap_buffers(window)

        time.sleep(0.02)

    glfw.terminate()


if __name__ == "__main__":
    main()
