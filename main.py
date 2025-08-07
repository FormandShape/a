import pyglet
from pyglet.gl import *

# Define the vertices of the cube
vertices = {
    'A': (1, 1, 1),
    'B': (1, 1, -1),
    'C': (1, -1, 1),
    'D': (1, -1, -1),
    'E': (-1, 1, 1),
    'F': (-1, 1, -1),
    'G': (-1, -1, 1),
    'H': (-1, -1, -1),
}

# Define the faces as triangles
faces = [
    ('B', 'C', 'E'),
    ('A', 'D', 'F'),
    ('A', 'D', 'G'),
    ('B', 'C', 'H'),
    ('A', 'F', 'G'),
    ('B', 'E', 'H'),
    ('C', 'E', 'H'),
    ('D', 'F', 'G'),
]

# Define the vertices and edges of the inner octahedron (intersection lines)
octa_vertices = {
    'px': (1, 0, 0), 'nx': (-1, 0, 0),
    'py': (0, 1, 0), 'ny': (0, -1, 0),
    'pz': (0, 0, 1), 'nz': (0, 0, -1),
}

octa_edges = [
    ('pz', 'py'), ('pz', 'ny'), ('pz', 'px'), ('pz', 'nx'),
    ('nz', 'py'), ('nz', 'ny'), ('nz', 'px'), ('nz', 'nx'),
    ('py', 'px'), ('py', 'nx'), ('ny', 'px'), ('ny', 'nx'),
]

class ViewerWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 200)

        # Rotation angles
        self.rx = self.ry = 0

        # Enable transparency
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        # Enable depth testing
        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.rx -= dy
            self.ry += dx

    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.gluPerspective(45, width / float(height), 0.1, 100.0)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)

    def on_draw(self):
        self.clear()
        pyglet.gl.glLoadIdentity()

        # Move the object away from the camera
        pyglet.gl.glTranslatef(0, 0, -5)

        # Apply rotation
        pyglet.gl.glRotatef(self.rx, 1, 0, 0)
        pyglet.gl.glRotatef(self.ry, 0, 1, 0)

        # Define some colors for the faces (with 0.5 alpha for transparency)
        colors = [
            (1, 0, 0, 0.5), (0, 1, 0, 0.5), (0, 0, 1, 0.5),
            (1, 1, 0, 0.5), (0, 1, 1, 0.5), (1, 0, 1, 0.5),
            (1, 0.5, 0, 0.5), (0.5, 1, 0.5, 0.5)
        ]

        # Draw the faces
        pyglet.gl.glBegin(pyglet.gl.GL_TRIANGLES)
        for i, face in enumerate(faces):
            color = colors[i % len(colors)]
            pyglet.gl.glColor4f(*color)
            for vertex_name in face:
                pyglet.gl.glVertex3fv(pyglet.gl.GLfloat(*vertices[vertex_name]))
        pyglet.gl.glEnd()

        # Draw the intersection lines (edges of the octahedron)
        pyglet.gl.glLineWidth(3)  # Make lines thicker
        pyglet.gl.glColor4f(0.1, 0.1, 0.1, 1.0)  # Dark, solid color
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        for edge in octa_edges:
            for vertex_name in edge:
                pyglet.gl.glVertex3fv(pyglet.gl.GLfloat(*octa_vertices[vertex_name]))
        pyglet.gl.glEnd()
        pyglet.gl.glLineWidth(1) # Reset line width

if __name__ == '__main__':
    window = ViewerWindow(width=800, height=600, caption='3D Viewer', resizable=True)
    pyglet.app.run()
