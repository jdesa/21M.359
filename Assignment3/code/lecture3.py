# lecture3.py

import sys
sys.path.append('common')
from core import *
from audio import *
from note import *

from kivy.core.window import Window
from kivy.clock import Clock as kivyClock
from kivy.uix.label import Label
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from random import random, randint
import numpy as np


##############################################################################

# basics of getting player input: 
# event-driven (touch_down, touch_up, touch_move)
# and polling/query (Window.mouse_pos)
class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()

      # create a label, keep track of it and add it so that it draws
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)
      self.audio = Audio()
      self.scaledegrees = ['1','2','3','4','5','6','7','8','9']
      self.majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]


   def on_touch_down(self, touch) :
      print 'down', touch.pos
      print "help!"
      octave = touch.pos[0] % 4 + 3
      interval = touch.pos[1] % 8
      self.audio.add_generator(NoteGenerator(5*12+interval, .5, 2.0, type = 'sine'))

   def on_touch_up(self, touch) :
      print 'up', touch.pos

   def on_touch_move(self, touch) :
      print 'move', touch.pos

   # called every frame to update stuff (like the label)
   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()


##############################################################################

# Drawing a circle.
class MainWidget2(BaseWidget) :
   def __init__(self):
      super(MainWidget2, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)
      self.audio = Audio()
      self.scaledegrees = ['1','2','3','4','5','6','7','8','9']
      self.majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]

   def on_touch_down(self, touch) :
      print 'down'

      # create a random color
      c = (random(), random(), random())
      clr = Color(*c)
      self.canvas.add(clr)

      # and a random radius:
      r = randint(10,60)
      p = touch.pos
      p = (touch.pos[0] - r, touch.pos[1] - r)

      elipse = Ellipse( pos=p, size=(r*2,r*2), segments = 40)
      self.canvas.add(elipse)

      octave = touch.pos[0] % 8
      interval = touch.pos[1] % 8
      self.audio.add_generator(NoteGenerator(octave*12+interval, .5, 2.0, type = 'sine'))


   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()



##############################################################################

# keeping track of a canvas instruction
class MainWidget3(BaseWidget) :
   def __init__(self):
      super(MainWidget3, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)

      # this color instruction is masked by the next one (self.color).
      # But if self.color is removed, this - Color(0,1,0) has effect.
      self.canvas.add(Color(0,1,0))

      self.color = Color(1,1,1)

      self.canvas.add(self.color)

   def on_touch_down(self, touch) :
      print 'down'

      # and a random radius:
      r = randint(10,60)
      p = touch.pos
      p = (touch.pos[0] - r, touch.pos[1] - r)
      self.canvas.add(Ellipse( pos=p, size=(r*2,r*2), segments = 20 ))


   def on_key_down(self, keycode, modifiers) :
      if keycode[1] == 'c':
         self.color.rgb = (random(), random(), random())

      if keycode[1] == 'v':
        self.canvas.add(Color(1,0,0))

      # self.canvas.clear() removes everything
      # self.canvas.remove(x) just removes one instruction
      if keycode[1] == 'z':
         self.canvas.remove(self.color)


   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()


##############################################################################

# KeyFrame Animation

class KFAnim(object):
   def __init__(self, xs, ys):
      super(KFAnim, self).__init__()
      self.xs = xs
      self.ys = ys
      
   def eval(self, t):
      return np.interp(t, self.xs, self.ys)


class Bubble(InstructionGroup):
   def __init__(self, pos, r, color):
      super(Bubble, self).__init__()

      self.pos = pos
      self.radius_anim = KFAnim((0, .1, 3), (r, 2*r, 0))
      self.x_anim = KFAnim((0, 3), (pos[0], 400))
      self.y_anim = KFAnim((0, 3), (pos[1], 300))

      self.color = Color(*color)
      self.circle = Ellipse(segments = 40)

      self.add(self.color)
      self.add(self.circle)

      self.time = 0
      self.on_update(0)

   def _set_pos(self, pos, radius):
      self.circle.pos = pos[0] - radius, pos[1] - radius
      self.circle.size = radius * 2, radius * 2

   def on_update(self, dt):
      self.time += dt

      # rad = self.radius_anim.eval(self.time)      
      # self._set_pos(self.pos, rad)

      pos = (self.x_anim.eval(self.time), self.y_anim.eval(self.time))
      rad = self.radius_anim.eval(self.time)      
      self._set_pos(pos, rad)

      # continue flag
      return self.time < 3.0


# keeping track of a canvas instruction
class MainWidget4(BaseWidget) :
   def __init__(self):
      super(MainWidget4, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)

      self.bubbles = []
      self.audio = Audio()
      self.scaledegrees = ['1','2','3','4','5','6','7','8','9']
      self.majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]
      self.bubblegendict = {}

   def on_touch_down(self, touch) :
      print 'down'

      # initial settings
      p = touch.pos
      r = randint(10,60)
      c = (random(), random(), random())
      bubble = Bubble(p, r, c)
      self.canvas.add(bubble)
      self.bubbles.append(bubble)
      
      octave = touch.pos[0] % 8
      interval = touch.pos[1] % 8
      gen = NoteGenerator((octave*12+interval))
      self.audio.add_generator(gen)
      self.bubblegendict[bubble] = gen

   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()
      self.info.text += '\nbubbles:%d' % len(self.bubbles)


      dt = kivyClock.frametime
      # for b in self.bubbles:
      #    b.on_update(dt)

      kill_list = [b for b in self.bubbles if b.on_update(dt) == False]
      for b in kill_list:
         self.bubbles.remove(b)
         self.canvas.remove(b)
         


##############################################################################

# Physics - based animation
class MainWidget5(BaseWidget) :
   def __init__(self):
      super(MainWidget5, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)

      self.bubbles = []
      self.audio = Audio()
      self.scaledegrees = ['1','2','3','4','5','6','7','8','9']
      self.majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]

   #Checks if a single bubble is in a state of collision with other bubbles
   def bubble_in_collision(self,bubble1):
      x1 = bubble1.pos[0]
      y1 = bubble1.pos[1]
      r1 = bubble1.radius
      for bubble2 in self.bubble_list:
         if bubble1 != bubble2:
            x2 = bubble2.pos[0]
            y2 = bubble2.pos[1]
            r2 = bubble2.radius
            distancebetween = np.sqrt((x1-x2)**2 + (y1-y2)**2) 
            combinedradius = r1+r2
            if distancebetween < combinedradius:
               return True
      return False

   def on_touch_down(self, touch) :
      p = touch.pos
      r = randint(10,60)
      c = (random(), random(), random())
      bubble = PhysBubble(p, r, c)
      #Check to make sure no other bubbles are in the current spawning point
      if not self.bubble_in_collision(bubble):
         self.canvas.add(bubble)
         self.bubbles.append(bubble)
               
   def bubblevbubble_collision(self, bubble_list):
      dt = kivyClock.frametime
      for bubble1 in bubble_list:
         x1 = bubble1.pos[0]
         y1 = bubble1.pos[1]
         r1 = bubble1.radius
         for bubble2 in bubble_list:
            if bubble1 != bubble2:
               x2 = bubble2.pos[0]
               y2 = bubble2.pos[1]
               r2 = bubble2.radius
               distancebetween = np.sqrt((x1-x2)**2 + (y1-y2)**2) 
               combinedradius = r1+r2
               if distancebetween < combinedradius:
                  bubble1.collision = True
                  bubble2.collision = True
                  bubble1.vel[0] = -bubble1.vel[0] * damping
                  bubble1.vel[1] = -bubble1.vel[1] * damping
                  bubble1.pos = bubble1.pos + bubble1.vel*dt

   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()
      self.info.text += '\nbubbles:%d' % len(self.bubbles)

      dt = kivyClock.frametime
      
      #Making the kill_list and bubble v bubble collision update
      self.bubble_list = []
      kill_list = []
      for bubble in self.bubbles:
         update = bubble.on_update(dt)
         if update[1] == False:
            kill_list.append(bubble)
         else:
            self.bubble_list.append((update[0]))
            if bubble.collision == True:
               bubble.collision = False
               interval = int(bubble.pos[0] / 100)
               gen =  NoteGenerator(60+interval, .5, .5, type = 'sine')
               self.audio.add_generator(gen)
      for bubble in kill_list:
         self.bubbles.remove(bubble)
         self.canvas.remove(bubble)

      self.bubblevbubble_collision(self.bubble_list)

gravity = np.array((0, -1800))


damping = 0.9
width = 800
maxnumcollisions = 8


class PhysBubble(InstructionGroup):
   def __init__(self, pos, r, color):
      super(PhysBubble, self).__init__()

      self.radius = r
      self.pos = np.array(pos, dtype=np.float64)
      self.vel = np.array((randint(-300, 300), randint(-100, 100)))

      self.color = Color(*color)
      self.circle = Ellipse(segments = 40)

      self.numcollisions = 0
      self.collision = False

      self.add(self.color)
      self.add(self.circle)

      self.on_update(0)


   def _set_pos(self, pos, radius):
      self.circle.pos = pos[0] - radius, pos[1] - radius
      self.circle.size = radius * 2, radius * 2

   def on_update(self, dt):
      if maxnumcollisions == self.numcollisions:
         return (self, False)

      # integrate accel to get vel
      self.vel += gravity * dt

      # integrate vel to get pos
      self.pos += self.vel * dt

      # collision with floor
      if self.pos[1] - self.radius < 0:
         self.vel[1] = -self.vel[1] * damping
         self.pos[1] = self.radius
         self.numcollisions += 1
         self.collision = True

      #collision with left wall
      if self.pos[0] - self.radius < 0:
         self.vel[0] = -self.vel[0] * damping
         self.pos[0] = self.radius
         self.numcollisions += 1
         self.collision = True

      #collision with right wall
      elif self.pos[0] + self.radius > width:
         self.vel[0] = -self.vel[0] * damping
         self.pos[0] = width - self.radius
         self.numcollisions += 1
         self.collision = True

      self._set_pos(self.pos, self.radius)

      return (self, True)

##############################################################################


class Flower(InstructionGroup):
   def __init__(self, pos, num_petals, radius, color):
      super(Flower, self).__init__()
      self.add(Color(*color))
      self.add(PushMatrix())
      self.add(Translate(*pos))
      
      self.rotate = Rotate(angle = 0)
      self.add(self.rotate)

      w = radius
      h = radius / num_petals**.5

      d_theta =  360. / num_petals
      for n in range(num_petals):
         self.add(Rotate(angle = d_theta))
         self.add(Translate(radius, 0))
         self.add(Ellipse(pos = (-w/2, -h/2), size = (w, h)))
         self.add(Translate(-radius, 0))

      self.add(PopMatrix())

   def on_update(self, dt):
      self.rotate.angle += 1.0

# keeping track of a canvas instruction
class MainWidget6(BaseWidget) :
   def __init__(self):
      super(MainWidget6, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)

      self.flowers = []

      flower = Flower((200, 300), 6, 80, (0, 1, 0))
      self.canvas.add(flower)
      self.flowers.append(flower)

      flower = Flower((500, 400), 10, 100, (1, 0.7, 0.7))
      self.canvas.add(flower)
      self.flowers.append(flower)

      self.on_update()


   def on_touch_down(self, touch) :
      pass

   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()
      
      for flower in self.flowers:
         flower.on_update(0)


run(MainWidget6)
