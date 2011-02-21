#!/usr/bin/python -O
# Run with python -O for massive performance gain on some platforms

from __future__ import division
from math import cos, pi, sin, sqrt
from random import seed, uniform, randint, gauss

from pyglet import clock, font, image, window
from pyglet.gl import *


class Position(object):

    @staticmethod
    def fromPolar(range, radians):
        x = range * sin(radians)
        y = range * cos(radians)
        return Position(x, y)

    @staticmethod
    def random(xcentre, ycentre, maxrange):
        range = sqrt(uniform(0, maxrange ** 2))
        radians = uniform(0, 2*pi)
        return Position.fromPolar(range, radians)

    def __init__(self, x, y, rot=None):
        self.x = x
        self.y = y
        if rot is None:
            self.rot = uniform(0, 2*pi)
        else:
            self.rot = rot


class Color(object):

    @staticmethod
    def random(r=None, g=None, b=None, a=None):
        if r is None:
            r = uniform(0, 1)
        if g is None:
            g = uniform(0, 1)
        if b is None:
            b = uniform(0, 1)
        return Color(r, g, b, a)

    def __init__(self, r, g, b, a=None):
        if a is None:
            print "none alpha"
            a = 1.0
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    rgba = property(lambda self: (self.r, self.g, self.b, self.a))


class Glyph(object):

    def __init__(self):
        self.numPetals = randint(3, 12)
        self.numShards = 64
        self.vertsGl = self.generateVerts()
        self.numVerts = len(self.vertsGl) // 2
        self.colorsGl = self.generateColors()

    def generateVerts(self):
        verts = [0.0, 0.0]
        tmp = 2 * pi / self.numShards
        for i in range(0, self.numShards + 1):
            bearing = i * tmp
            radius = sqrt(abs(sin(tmp * i * self.numPetals / 2.0) + 0.2))
            pos = Position.fromPolar(radius, bearing)
            verts.extend([pos.x, pos.y])
        return (GLfloat * len(verts))(*verts)

    def generateColors(self):
        basic1 = Color.random(a=0.5)
        basic2 = Color.random(a=0.5)
        colors = [1.0, 1.0, 1.0, 1.0]
        tmp = 2 * pi / self.numShards
        for i in range(0, self.numVerts):
            wave = sin(i * tmp * self.numPetals / 2.0) / 2.0
            i1 = 0.5 + wave
            i2 = 0.5 - wave
            r = basic1.r * i1 + basic2.r * i2
            g = basic1.g * i1 + basic2.g * i2
            b = basic1.b * i1 + basic2.b * i2
            colors.extend([r, g, b, 0.25])
        return (GLfloat * len(colors))(*colors)

    def draw(self):
        glColorPointer(4, GL_FLOAT, 0, self.colorsGl)
        glVertexPointer(2, GL_FLOAT, 0, self.vertsGl)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.numVerts)


class Entity(object):

    nextId = 0
    nextGrowAt = 0.0

    def __init__(self, pos, size):
        self.id = Entity.nextId
        Entity.nextId += 1
        self.pos = pos
        self.dRot = uniform(-10, 10)
        self.size = size
        self.maxSize = uniform(1, 1.7) ** 2
        self.glyph = Glyph()
        self.growAt = World.age + Entity.nextGrowAt
        Entity.nextGrowAt += uniform(0, 1.0 / (self.id + 1))

    def tick(self, dt):
        self.pos.rot += self.dRot * dt
        if self.growAt < World.age:
            self.size *= 1.0 + (self.maxSize - self.size) * dt

    def draw(self):
        if self.growAt < World.age:
            glPushMatrix()
            glTranslatef(self.pos.x, self.pos.y, 0)
            glRotatef(self.pos.rot, 0, 0, 1)
            glScalef(self.size, self.size, 1)
            self.glyph.draw()
            glPopMatrix()


class World(object):

    numEnts = 800
    age = 0.0

    def __init__(self):
        self.ents = {}
        for id in range(self.numEnts):
            self.spawnEntity()

    def spawnEntity(self):
        size = 0.01
        pos = Position(uniform(-16, 16), uniform(-10, 10))
        ent = Entity(pos, size)
        self.ents[ent.id] = ent

    def tick(self, dt):
        World.age += dt
        for ent in self.ents.values():
            ent.tick(dt)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW);

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        for ent in self.ents.values():
            ent.draw()


class Camera(object):

    def __init__(self, win, world, x=0, y=0, rot=0, zoom=1):
        self.win = win
        self.world = world
        self.pos = Position(x, y, rot)
        self.zoom = zoom
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 0.0)

    def worldProjection(self):
        glEnable(GL_BLEND)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        widthRatio = self.win.width / self.win.height
        gluOrtho2D(
            -self.zoom * widthRatio,
            self.zoom * widthRatio,
            -self.zoom,
            self.zoom)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(
            self.pos.x, self.pos.y, -1.0,
            self.pos.x, self.pos.y, 1.0,
            sin(self.pos.rot), cos(self.pos.rot), 0.0)

    def hudProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.win.width, 0, self.win.height)


class Hud(object):

    def __init__(self, win, world):
        helv = font.load('Helvetica', 30)
        message = '%d entities' % (world.numEnts)
        self.text = font.Text(
            helv,
            message,
            x=win.width,
            y=0,
            halign=font.Text.RIGHT,
            valign=font.Text.BOTTOM,
            color=(1, 1, 1, 0.5),
        )
        self.fps = clock.ClockDisplay(
            format="%(fps).1ffps",
            font=helv)

    def draw(self):
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
        # self.text.draw()
        self.fps.draw()


class App(object):

    def __init__(self):
        # seed(0)
        self.world = World()
        self.win = window.Window(fullscreen=True, vsync=True)
        self.camera = Camera(self.win, self.world, zoom=10)
        self.hud = Hud(self.win, self.world)

    def mainLoop(self):
        clock.tick()
        while not self.win.has_exit:
            self.win.dispatch_events()

            dt = clock.tick()
            self.world.tick(dt)

            if World.age > 4.0:
               self.camera.zoom *= 1 - (min(5.0, World.age) - 4.0) / 20.0 * dt

            self.camera.worldProjection()
            self.world.draw()

            self.camera.hudProjection()
            self.hud.draw()

            self.win.flip()

app = App()
app.mainLoop()

