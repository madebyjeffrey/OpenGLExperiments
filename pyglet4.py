from __future__ import division
from __future__ import print_function

from pyglet import clock, font, image, window, text
from pyglet.gl import *


import numpy

SIZE = 64
TWO_PI = 2.0 * 3.1415926535


class World(object):
    def __init__(self):
        self.verts_id = GLuint()
        glGenBuffers(1, self.verts_id)
        self.mesh = []
        for x in xrange(SIZE):
            for z in xrange(SIZE):
                self.mesh.extend((float(SIZE//2 - x), 0.0, float(SIZE//2 - z)))
        data = (GLfloat*len(self.mesh))(*self.mesh)
        glBindBuffer(GL_ARRAY_BUFFER, self.verts_id)
        glBufferData(GL_ARRAY_BUFFER, len(data)*4, data, GL_STATIC_DRAW)       

        self.index_id = GLuint()
        glGenBuffers(1, self.index_id)
        self.index = []
        for x in xrange(SIZE-1):
            for z in xrange(SIZE-1):
                self.index.extend((x*SIZE+z, x*SIZE+z+1, (x+1)*SIZE+z))
                self.index.extend((x*SIZE+z+1, (x+1)*SIZE+z, (x+1)*SIZE+z+1))
        data = (GLushort*len(self.index))(*self.index)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(data)*2, data, GL_STATIC_DRAW)        

        
    def draw(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
    
        gluLookAt(0.0, 25.0, -45.0, 0.0, 0.0, 0.0, 0, 1, 0)
    
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.verts_id)
        glVertexPointer(3, GL_FLOAT, 0, 0)

        glEnableClientState(GL_INDEX_ARRAY)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_id)
        glDrawElements(GL_TRIANGLES, len(self.index), GL_UNSIGNED_SHORT, 0)

        glFlush()
                


class Camera(object):
    def __init__(self, win, world, x=0, y=0, rot=0, zoom=1):
        self.win = win
        self.world = world
#        self.pos = Position(x, y, rot)
        self.zoom = zoom
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 0)
        
    def worldProjection(self):
        glEnable(GL_BLEND)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90.0, self.win.width/float(self.win.height), 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0.0, 25.0, -45.0, 0.0, 0.0, 0.0, 0, 1, 0)
        
    def hudProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.win.width, 0, self.win.height)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
class Hud(object):
    def __init__(self, win, world):
        helv = font.load('Helvetica', 30)
        self.fpsLabel = text.Label('', font_name='Helvetica', x=60, y=60)
        self.fps = clock.ClockDisplay(
            format = "%(fps).1ffps", font=helv)
        self.fps.label = self.fpsLabel
            
    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.fpsLabel.text = ("%.1f" % clock.get_fps())
        self.fpsLabel.draw()
        

class App(object):
    def __init__(self):
        self.world = World()
        self.config = Config(double_buffer = True)
        self.win = window.Window(800, 600, 
                                caption="Terrain 4",
                                vsync = True,
                                config = self.config)
        self.camera = Camera(self.win, self.world, zoom=10)
        self.hud = Hud(self.win, self.world)
        
    def mainLoop(self):
        clock.tick()
        while not self.win.has_exit:
            self.win.dispatch_events()
            
#            self.win.clear()
            #dt = clock.tick()
            #self.world.tick(dt)
            clock.tick()
            
            self.camera.worldProjection()
            self.world.draw()
            
            self.camera.hudProjection()
            self.hud.draw()
            
            self.win.flip()
  
if __name__ == '__main__':
    app = App()
    app.mainLoop()
#    pyglet.app.run()

