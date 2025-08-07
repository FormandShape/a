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
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable depth testing
        glEnable(GL_DEPTH_TEST)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            self.rx -= dy
            self.ry += dx

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def on_draw(self):
        self.clear()
        glLoadIdentity()

        # Move the object away from the camera
        glTranslatef(0, 0, -5)

        # Apply rotation
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)

        # Define some colors for the faces (with 0.5 alpha for transparency)
        colors = [
            (1, 0, 0, 0.5), (0, 1, 0, 0.5), (0, 0, 1, 0.5),
            (1, 1, 0, 0.5), (0, 1, 1, 0.5), (1, 0, 1, 0.5),
            (1, 0.5, 0, 0.5), (0.5, 1, 0.5, 0.5)
        ]

        # Draw the faces
        glBegin(GL_TRIANGLES)
        for i, face in enumerate(faces):
            color = colors[i % len(colors)]
            glColor4f(*color)
            for vertex_name in face:
                glVertex3fv(GLfloat(*vertices[vertex_name]))
        glEnd()

        # Draw the intersection lines (edges of the octahedron)
        glLineWidth(3)  # Make lines thicker
        glColor4f(0.1, 0.1, 0.1, 1.0)  # Dark, solid color
        glBegin(GL_LINES)
        for edge in octa_edges:
            for vertex_name in edge:
                glVertex3fv(GLfloat(*octa_vertices[vertex_name]))
        glEnd()
        glLineWidth(1) # Reset line width

if __name__ == '__main__':
    window = ViewerWindow(width=800, height=600, caption='3D Viewer', resizable=True)
    pyglet.app.run()
