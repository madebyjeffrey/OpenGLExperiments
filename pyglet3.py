
from pyglet import clock, font, image, window, text
from pyglet.gl import *


import numpy

SIZE = 64
TWO_PI = 2.0 * 3.1415926535


class World(object):
    def __init__(self):
        self.mesh = numpy.zeros((SIZE, SIZE, 3), 'f')
        
        for x in xrange(SIZE):
            for z in xrange(SIZE):
                self.mesh[x][z][0] = float ((SIZE/2) -x) # centre around origin
                self.mesh[x][z][1] = 0.0;
                self.mesh[x][z][2] = float((SIZE / 2) -z)
        
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
    
        gluLookAt(0.0, 25.0, -45.0, 0.0, 0.0, 0.0, 0, 1, 0)
    
        for x in xrange (SIZE - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for z in xrange (SIZE - 1):
                glVertex3f(self.mesh[x][z][0], self.mesh[x][z][1], self.mesh[x][z][2])
                glVertex3f(self.mesh[x+1][z][0], self.mesh[x+1][z][1], self.mesh[x+1][z][2])
                
            glEnd()
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
    
class Hud(object):
    def __init__(self, win, world):
        helv = font.load('Helvetica', 30)
        self.fpsLabel = text.Label('', font_name='Helvetica', x=10, y=10)
        self.fps = clock.ClockDisplay(
            format = "%(fps).1ffps", font=helv)
        self.fps.label = self.fpsLabel
            
    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.fps.draw()

class App(object):
    def __init__(self):
        self.world = World()
        self.config = Config(double_buffer = True)
        self.win = window.Window(800, 600, 
                                caption="Terrain 3",
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
            
            self.camera.worldProjection()
            self.world.draw()
            
            self.camera.hudProjection()
            self.hud.draw()
            
            self.win.flip()
  
if __name__ == '__main__':
    app = App()
    app.mainLoop()
#    pyglet.app.run()

