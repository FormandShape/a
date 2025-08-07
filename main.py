import pyglet
from pyglet.gl import *
from pyglet import math

# --- Data Restructuring for Modern OpenGL ---

# (Previous data restructuring code remains the same)
# Original vertices
_vertices = {
    'A': (1, 1, 1), 'B': (1, 1, -1), 'C': (1, -1, 1), 'D': (1, -1, -1),
    'E': (-1, 1, 1), 'F': (-1, 1, -1), 'G': (-1, -1, 1), 'H': (-1, -1, -1),
}
# Original faces (triangles)
_faces = [
    ('B', 'C', 'E'), ('A', 'D', 'F'), ('A', 'D', 'G'), ('B', 'C', 'H'),
    ('A', 'F', 'G'), ('B', 'E', 'H'), ('C', 'E', 'H'), ('D', 'F', 'G'),
]
# We need to create un-indexed data for flat colors per face
face_drawing_data = []
color_drawing_data = []
_face_colors = [
    (1, 0, 0, 0.2), (0, 1, 0, 0.2), (0, 0, 1, 0.2), (1, 1, 0, 0.2),
    (0, 1, 1, 0.2), (1, 0, 1, 0.2), (1, 0.5, 0, 0.2), (0.5, 1, 0.5, 0.2)
]
for i, face in enumerate(_faces):
    color = _face_colors[i % len(_face_colors)]
    for vertex_name in face:
        face_drawing_data.extend(_vertices[vertex_name])
        color_drawing_data.extend(color)

# Data for the intersection lines (octahedron)
_octa_vertices = {
    'px': (1, 0, 0), 'nx': (-1, 0, 0), 'py': (0, 1, 0),
    'ny': (0, -1, 0), 'pz': (0, 0, 1), 'nz': (0, 0, -1),
}
_octa_edges = [
    ('pz', 'py'), ('pz', 'ny'), ('pz', 'px'), ('pz', 'nx'),
    ('nz', 'py'), ('nz', 'ny'), ('nz', 'px'), ('nz', 'nx'),
    ('py', 'px'), ('py', 'nx'), ('ny', 'px'), ('ny', 'nx'),
]
line_vertex_data = []
line_color_data = []
line_color = (0.1, 0.1, 0.1, 1.0)
for edge in _octa_edges:
    for vertex_name in edge:
        line_vertex_data.extend(_octa_vertices[vertex_name])
        line_color_data.extend(line_color)

# Data for the wireframe cube
_cube_edges = [
    ('A', 'B'), ('B', 'D'), ('D', 'C'), ('C', 'A'), # Top face
    ('E', 'F'), ('F', 'H'), ('H', 'G'), ('G', 'E'), # Bottom face
    ('A', 'E'), ('B', 'F'), ('C', 'G'), ('D', 'H')  # Connecting edges
]
cube_vertex_data = []
cube_color_data = []
cube_color = (0.8, 0.8, 0.8, 0.2) # Light grey, 0.2 alpha
for edge in _cube_edges:
    for vertex_name in edge:
        cube_vertex_data.extend(_vertices[vertex_name])
        cube_color_data.extend(cube_color)


# --- Shader Definitions ---
vert_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec4 aColor;
out vec4 vertexColor;
uniform mat4 mvp;

void main()
{
    gl_Position = mvp * vec4(aPos, 1.0);
    vertexColor = aColor;
}
"""

frag_shader_source = """
#version 330 core
in vec4 vertexColor;
out vec4 FragColor;

void main()
{
    FragColor = vertexColor;
}
"""

def create_shader_program(vertex_source, fragment_source):
    """Compiles and links a shader program using Pyglet's high-level API."""
    vertex_shader = pyglet.graphics.shader.Shader(vertex_source, 'vertex')
    fragment_shader = pyglet.graphics.shader.Shader(fragment_source, 'fragment')
    return pyglet.graphics.shader.ShaderProgram(vertex_shader, fragment_shader)


class ViewerWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 200)

        # --- Shader and Buffer Setup ---
        self.shader_program = create_shader_program(vert_shader_source, frag_shader_source)

        # --- Set up VAO for faces ---
        self.face_vao = GLuint()
        glGenVertexArrays(1, self.face_vao)
        glBindVertexArray(self.face_vao)
        # Position buffer
        face_vbo_pos = GLuint()
        glGenBuffers(1, face_vbo_pos)
        glBindBuffer(GL_ARRAY_BUFFER, face_vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, len(face_drawing_data) * 4, (GLfloat * len(face_drawing_data))(*face_drawing_data), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(0)
        # Color buffer
        face_vbo_color = GLuint()
        glGenBuffers(1, face_vbo_color)
        glBindBuffer(GL_ARRAY_BUFFER, face_vbo_color)
        glBufferData(GL_ARRAY_BUFFER, len(color_drawing_data) * 4, (GLfloat * len(color_drawing_data))(*color_drawing_data), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(1)
        self.face_vertex_count = len(face_drawing_data) // 3

        # --- Set up VAO for lines ---
        self.line_vao = GLuint()
        glGenVertexArrays(1, self.line_vao)
        glBindVertexArray(self.line_vao)
        # Position buffer
        line_vbo_pos = GLuint()
        glGenBuffers(1, line_vbo_pos)
        glBindBuffer(GL_ARRAY_BUFFER, line_vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, len(line_vertex_data) * 4, (GLfloat * len(line_vertex_data))(*line_vertex_data), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(0)
        # Color buffer
        line_vbo_color = GLuint()
        glGenBuffers(1, line_vbo_color)
        glBindBuffer(GL_ARRAY_BUFFER, line_vbo_color)
        glBufferData(GL_ARRAY_BUFFER, len(line_color_data) * 4, (GLfloat * len(line_color_data))(*line_color_data), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(1)
        self.line_vertex_count = len(line_vertex_data) // 3

        # --- Set up VAO for cube ---
        self.cube_vao = GLuint()
        glGenVertexArrays(1, self.cube_vao)
        glBindVertexArray(self.cube_vao)
        # Position buffer
        cube_vbo_pos = GLuint()
        glGenBuffers(1, cube_vbo_pos)
        glBindBuffer(GL_ARRAY_BUFFER, cube_vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, len(cube_vertex_data) * 4, (GLfloat * len(cube_vertex_data))(*cube_vertex_data), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(0)
        # Color buffer
        cube_vbo_color = GLuint()
        glGenBuffers(1, cube_vbo_color)
        glBindBuffer(GL_ARRAY_BUFFER, cube_vbo_color)
        glBufferData(GL_ARRAY_BUFFER, len(cube_color_data) * 4, (GLfloat * len(cube_color_data))(*cube_color_data), GL_STATIC_DRAW)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, 0)
        glEnableVertexAttribArray(1)
        self.cube_vertex_count = len(cube_vertex_data) // 3

        glBindVertexArray(0)

        # --- GL Settings and Matrices ---
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.rx = 45  # Initial rotation
        self.ry = 45

        self.proj_matrix = math.Mat4()
        self.view_matrix = math.Mat4.from_translation(math.Vec3(0, 0, -5))

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        self.proj_matrix = math.Mat4.perspective_projection(aspect=width/height, z_near=0.1, z_far=100, fov=45)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            sensitivity = 0.5
            self.rx -= dy * sensitivity
            self.ry += dx * sensitivity

    def on_draw(self):
        self.clear()

        # Use the shader program
        self.shader_program.use()

        # Create model matrix from rotation
        model_matrix = math.Mat4.from_rotation(self.rx, (1, 0, 0))
        model_matrix @= math.Mat4.from_rotation(self.ry, (0, 1, 0))

        # Calculate final MVP matrix and set uniform
        mvp = self.proj_matrix @ self.view_matrix @ model_matrix
        self.shader_program['mvp'] = mvp

        # Draw faces
        glBindVertexArray(self.face_vao)
        glDrawArrays(GL_TRIANGLES, 0, self.face_vertex_count)

        # Draw the wireframe cube
        glLineWidth(1)
        glBindVertexArray(self.cube_vao)
        glDrawArrays(GL_LINES, 0, self.cube_vertex_count)

        # Draw intersection lines (thicker)
        glLineWidth(3)
        glBindVertexArray(self.line_vao)
        glDrawArrays(GL_LINES, 0, self.line_vertex_count)
        glLineWidth(1)

        self.shader_program.stop()


if __name__ == '__main__':
    config = pyglet.gl.Config(major_version=3, minor_version=3, depth_size=24)
    window = ViewerWindow(width=800, height=600, caption='Modern OpenGL Viewer', resizable=True, vsync=True, config=config)
    pyglet.app.run()
