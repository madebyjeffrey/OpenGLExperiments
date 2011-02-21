#
# Copyright Tristam Macdonald 2008.
#
# Distributed under the Boost Software License, Version 1.0
# (see http://www.boost.org/LICENSE_1_0.txt)
#
 
import random, math
import pyglet
from pyglet.gl import *
# create the window, but keep it offscreen until we are done with setup

window = pyglet.window.Window(640, 480, visible=False, caption="Pong")
# centre the window on whichever screen it is currently on (in case of multiple monitors)

window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)
# create a batch to perform all our rendering
batch = pyglet.graphics.Batch()
# paddles are subclassed from Sprite, to ease drawing
class Paddle(pyglet.sprite.Sprite):
    def __init__(self, x, y):
        # build a solid white image for the paddle
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        image = pyglet.image.create(8, 64, pattern)
 
        # offset our image to centre it
        image.anchor_x, image.anchor_y = 4, 32
 
        #pass it all on to the superclass constructor
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch=batch)
 
# mostly identical to Paddle, apart from size, offsets and velocity
class Ball(pyglet.sprite.Sprite):
    def __init__(self):
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        image = pyglet.image.create(8, 8, pattern)
        image.anchor_x, image.anchor_y = 4, 4
        pyglet.sprite.Sprite.__init__(self, image, batch=batch)
        # reset ourselves
        self.reset()
    def reset(self):
        # place ourselves in the centre of the playing field
        self.x, self.y = 400, 250
        # give ourselves a random direction within 45 degrees of either paddle
        angle = random.random()*math.pi/2 + random.choice([-math.pi/4, 3*math.pi/4])
        # convert that direction into a velocity
        self.vx, self.vy = math.cos(angle)*300, math.sin(angle)*300
 
# handle the window resize event
@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # setup a fixed dimension orthographic projection
    # this avoids gameplay problems if the window resolution is changed
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # tell pyglet that we have handled the event, prevents the default handler from running
    return pyglet.event.EVENT_HANDLED
 
# setup a key handler to track keyboard input
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)
 
# setup a stack for our game states
states = []
 
# this game state does nothing until the space bar is pressed
# at which point it returns control to the previous state
class PausedState:
    def update(self, dt):
        if keymap[pyglet.window.key.SPACE]:
            states.pop()
 
# this class plays the actual game
class GameState:
    def __init__(self):
        # setup the static player names
        pyglet.text.Label('PLAYER', font_name='Arial', font_size=24, x=200, y=575, anchor_x='center', anchor_y='center', batch=batch)
        pyglet.text.Label('CPU', font_name='Arial', font_size=24, x=600, y=575, anchor_x='center', anchor_y='center', batch=batch)
 
        # setup the dynamic score fields
        self.player_label = pyglet.text.Label('000', font_name='Arial', font_size=24, x=200, y=525, anchor_x='center', anchor_y='center', batch=batch)
        self.cpu_label = pyglet.text.Label('000', font_name='Arial', font_size=24, x=600, y=525, anchor_x='center', anchor_y='center', batch=batch)
 
        # setup the divider between the play area and the score area
        batch.add(2, GL_LINES, None, ('v2i', (0,500, 800,500)))
 
        # scores start at zero
        self.player_score = 0
        self.cpu_score = 0
 
        #   initliase the paddles in the correct locations
        self.p1 = Paddle(4, 250)
        self.p2 = Paddle(800-4, 250)
 
        # add the ball
        self.b = Ball()
 
    # used to reset the ball and paddle locations between rounds
    def reset(self):
        self.p1.y = 250
        self.p2.y = 250
 
        self.b.reset()
 
    # moves the player paddle based on keyboard input
    def handle_player(self, dt):
        if keymap[pyglet.window.key.UP]:
            self.p1.y += 400*dt
        elif keymap[pyglet.window.key.DOWN]:
            self.p1.y -= 400*dt
 
    # moves the CPU paddle with some semblence of inteligence
    def handle_ai(self, dt):
        if self.b.vx > 0:
            diff = self.b.y - self.p2.y
            self.p2.y += (diff if diff < 400*dt else 400*dt)
 
    def update(self, dt):
        # move the ball according to simple physics
        self.b.x += self.b.vx * dt
        self.b.y += self.b.vy * dt
 
        # allow the paddles to move
        self.handle_player(dt)
        self.handle_ai(dt)
 
        # prevent the paddles from leaving the playing area
        for p in [self.p1, self.p2]:
            if p.y > 500-32:
                p.y = 500-32
            elif p.y < 32:
                p.y = 32
 
        # reflect the ball if is in contact with the top of the playing area
        if self.b.y > 500-4:
            self.b.y = 500-4
            self.b.vy = -self.b.vy
        # and the same for the bottom
        elif self.b.y < 4:
            self.b.y = 4
            self.b.vy = -self.b.vy
 
        # reflect the ball off of the CPU paddle if it is in contact
        if self.b.x > 800-8 and self.b.y <= self.p2.y+32 and self.b.y >= self.p2.y-32:
            self.b.x = 800-8
            self.b.vx = -self.b.vx
            # change the velocity based on the distance to the center of the paddle
            self.b.vy += (self.b.y - self.p2.y)/2
        # and the same for the player paddle
        elif self.b.x < 8 and self.b.y <= self.p1.y+32 and self.b.y >= self.p1.y-32:
            self.b.x = 8
            self.b.vx = -self.b.vx
            self.b.vy += (self.b.y - self.p1.y)/2
 
        # if the ball escapes the side of the play area, declare victory
        if self.b.x < 0 or self.b.x > 800:
            # if the ball left the player side, score for the cpu
            if self.b.x < 0:
                global cpu_score
                self.cpu_score += 5
                self.cpu_label.text = '%03d' % self.cpu_score
            # otherwise, score for the player
            else:
                global player_score
                self.player_score += 5
                self.player_label.text = '%03d' % self.player_score
 
            # reset the ball and paddle locations
            self.reset()
            # pause the game befor the next round
            states.append(PausedState())
 
# clear the window and draw the scene
@window.event
def on_draw():
    window.clear()
 
    batch.draw()
 
# update callback
def update(dt):
    # update the topmost state, if we have any
    if len(states):
        states[-1].update(dt)
    # otherwise quit
    else:
        pyglet.app.exit()
 
# setup the inital states
states.append(GameState())
# game starts paused
states.append(PausedState())
 
# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)
 
# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()
window.flip()
 
# make the window visible at last
window.set_visible(True)
 
# finally, run the application
pyglet.app.run()
