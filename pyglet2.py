
import pyglet

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

SIZE = 64
TWO_PI = 2.0 * 3.1415926535

def initGL(width, height):
    global g_mesh
    
    glClearColor(0.0, 0.0, 0.0, 0.5)
    glClearDepth(1.0)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_DEPTH_TEST)

    glColor(1.0, 1.0, 1.0, 1.0)
    # wire frame mode
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    g_mesh = numpy.zeros((SIZE, SIZE, 3), 'f')
    
    for x in xrange(SIZE):
        for z in xrange(SIZE):
            g_mesh[x][z][0] = float ((SIZE/2) -x) # centre around origin
            g_mesh[x][z][1] = 0.0;
            g_mesh[x][z][2] = float((SIZE / 2) -z)
    
    return True

window = pyglet.window.Window(800,600, caption="Terrain")

window.context.set_current()

initGL(800, 600)


label = pyglet.text.Label('Hail',
                            font_name='Arial',
                            font_size=36,
                            x=window.width//2, y=window.height//2,
                            anchor_x='center', anchor_y='center')

    
    
@window.event
def on_draw():
    global g_mesh
    
    window.clear()
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    gluLookAt(0.0, 25.0, -45.0, 0.0, 0.0, 0.0, 0, 1, 0)
    
    for x in xrange (SIZE - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for z in xrange (SIZE - 1):
            glVertex3f(g_mesh[x][z][0], g_mesh[x][z][1], g_mesh[x][z][2])
            glVertex3f(g_mesh[x+1][z][0], g_mesh[x+1][z][1], g_mesh[x+1][z][2])
            
        glEnd()
    glFlush()
    
    window.flip()
#    label.draw()
    
if __name__ == '__main__':
    pyglet.app.run()

