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
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from random import random, randint
import numpy as np

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
      self.wavetype = 'sine'

   def on_touch_down(self, touch) :
      print 'down'

      # initial settings
      p = touch.pos
      r = randint(10,60)

      
      interval = int(touch.pos[0] / (width/8)) 
      octave = int(touch.pos[1] / (height/3))
      pitch = 48+12*octave+interval
      print "octave: " + str(octave) + " interval: " +str(interval) +  " pitch: " + str(pitch)
      gen = NoteGenerator(pitch, .5, 3.0, self.wavetype)
      self.audio.add_generator(gen)

      self.colors = [(178, 18, 18, 1.0), (255, 252, 25, 1.0), (255, 0, 0, 1.0), (20,133,204, 1.0), (9,113,178, 1.0), (0,78,127, 1.0), (13,161,254, 1.0), (178, 18, 18, 1.0)]
      color = self.colors[interval]
      print color
      bubble = Bubble(p, r, color)
      self.canvas.add(bubble)
      self.bubbles.append(bubble)

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

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == "m":
         self.wavetype = "sine"
      elif keycode[1] == ",":
         self.wavetype = "tri"
      elif keycode[1] == ".":
         self.wavetype = "square"
      elif keycode[1] == "/":
         self.wavetype = "saw"
         
##############################################################################

# Physics - based animation
class MainWidget5(BaseWidget) :
   def __init__(self):
      super(MainWidget5, self).__init__()
      self.info = Label(text = "text", pos=(0, 500), text_size=(100,100), valign='top')
      self.add_widget(self.info)
      self.wavetype ='sine'
      self.bubbles = []
      self.audio = Audio()
      self.scaledegrees = ['1','2','3','4','5','6','7','8','9']
      self.majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]
      self.instructions1 = Label(text = "Tap enter to turn bubble absorb mode on and off.", pos=(500, 500), text_size=(800,100), valign='top', markup=True)
      self.add_widget(self.instructions1)
      self.bubbleabsorbon = False


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

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'enter':
         self.bubbleabsorbon = not self.bubbleabsorbon

  
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

   def bubbleabsorb(self, bubble_list):
      dt = kivyClock.frametime
      for bubble1 in bubble_list:
         x1 = bubble1.pos[0]
         y1 = bubble1.pos[1]
         r1 = bubble1.radius
         for bubble2 in bubble_list:
            if bubble1 != bubble2 and not bubble1.collisionchecked and not bubble2.collisionchecked:
               
               x2 = bubble2.pos[0]
               y2 = bubble2.pos[1]
               r2 = bubble2.radius
               distancebetween = np.sqrt((x1-x2)**2 + (y1-y2)**2) 
               combinedradius = r1+r2
               
               if distancebetween < combinedradius:
                  
                  xmult = 1.0 if np.sign(bubble1.vel[0]) == np.sign(bubble2.vel[0]) else -1.0
                  ymult = 1.0 if np.sign(bubble1.vel[1]) == np.sign(bubble2.vel[1]) else -1.0

                  print "xmult is: " + str(xmult)
                  print "ymult is: " + str(ymult)

                  bubble1.collisionchecked = True
                  bubble2.collisionchecked = True

                  bubble1.vel[0] += xmult*bubble1.vel[0]*damping
                  bubble2.vel[0] += ymult*bubble2.vel[0]*damping
                  bubble1.vel[1] += xmult*bubble1.vel[1]*damping
                  bubble2.vel[1] += ymult*bubble2.vel[1]*damping

                  fx = 100000 * (combinedradius - abs(x2 - x1))
                  fy = 100000 * (combinedradius - abs(y2 - y1))
                   
                  xmult = 1.0 if np.sign(bubble1.vel[0]) == np.sign(bubble2.vel[0]) else -1.0
                  ymult = 1.0 if np.sign(bubble1.vel[1]) == np.sign(bubble2.vel[1]) else -1.0

                  bubble1.vel[0] += np.sign(x2-x1)*abs(fx)*dt/(r1**2.0)
                  bubble1.vel[1] += np.sign(y2-y1)*abs(fy)*dt/(r1**2.0)
                  bubble2.vel[0] += np.sign(x2-x1)*abs(fx)*dt/(r2**2.0)
                  bubble2.vel[1] += np.sign(y2-y1)*abs(fy)*dt/(r2**2.0)

                  bubble1.vel = np.clip(bubble1.vel, -100, 100)
                  bubble2.vel = np.clip(bubble2.vel, -100, 100)

                  bubble1.collision = True
                  
            
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
               bubble.interval = int(bubble.pos[0] / 100)
               gen =  NoteGenerator(60+bubble.interval, .5, .5, type = bubble.wavetype)
               print bubble.wavetype
               print self.audio.generators
               self.audio.add_generator(gen)
      
      for bubble in kill_list:
         self.bubbles.remove(bubble)
         self.canvas.remove(bubble)

      if self.bubbleabsorbon:
         self.bubbleabsorb(self.bubble_list)
      else:
         self.bubblevbubble_collision(self.bubble_list)

gravity = np.array((0, -1800))


damping = 0.9
width = 800
height = 600
maxnumcollisions = 8


class PhysBubble(InstructionGroup):
   def __init__(self, pos, r, color):
      super(PhysBubble, self).__init__()

      self.collisionchecked = False
      self.radius = r
      self.pos = np.array(pos, dtype=np.float64)
      self.vel = np.array((randint(-300, 300), randint(-100, 100)))

      self.color = Color(*color)
      self.circle = Ellipse(segments = 40)

      self.numcollisions = 0
      self.collision = False

      self.add(self.color)
      self.add(self.circle)

      self.interval = 0

      self.wavetypes = ['sine','square','saw','tri']
      self.wavetype = self.wavetypes[self.numcollisions%4]
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

      elif self.pos[1] - self.radius > height:
         self.vel[1] = -self.vel[1] * damping
         self.pos[1] = height-self.radius
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

      self.collisionchecked = False


      self._set_pos(self.pos, self.radius)

      return (self, True)

##############################################################################

##############################################################################

class Flower(InstructionGroup):
   def __init__(self, pos, num_petals, radius, color, key):
      super(Flower, self).__init__()
      self.add(Color(*color))
      self.add(PushMatrix())
      self.add(Translate(*pos))

      self.rotate = Rotate(angle = 0)
      self.add(self.rotate)

      self.button = Button(text="Hello World", pos =(pos[0] - 50, pos[1] - 50), font_size=14, background_color = (0,0,0,0), border=(30, 30, 30, 30))

      self.active = True
      self.key = key

      w = radius
      h = radius / num_petals**.5

      self.petal_rotations = []
      d_theta =  360. / num_petals

      color = Color(np.random.rand(),np.random.rand(), np.random.rand(),.1)
      self.add(Ellipse(pos = (-50, -50), size = (100, 100)))

      majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]

      self.petals = {}
      for n in range(num_petals):
         angle = d_theta*n
         note = [self.key+majorkeyintervals[n%len(majorkeyintervals)] + n/len(majorkeyintervals) * 12, .5, .5, 'sine']
         color = Color(np.random.rand(),np.random.rand(), np.random.rand(),.1)
         self.add(color)
         self.add(Rotate(angle = d_theta))
         self.add(Translate(radius, 0))
         ellipse = Ellipse(pos = (-w/2, -h/2), size = (w, h))
         self.add(ellipse)
         self.add(Translate(-radius, 0)) 
         
         self.petals[angle] = [note, color, ellipse]

      self.add(PopMatrix())

   def on_update(self, dt, rps):
      if self.active:
         print "dt is: " + str(dt)
         self.rotate.angle += int(dt*rps*360.0) #Rotations/second. #Todo: make this rotations per second

width = 800
height = 600

waveform_dict = {"m":"sine", ",":"square", ".":"saw", "/":"tri"}

# keeping track of a canvas instruction
class MainWidget6(BaseWidget) :
   def __init__(self):
      super(MainWidget6, self).__init__()
      self.info = Label(text = "text", pos=(0, 460), text_size=(100,100), valign='top')
      self.add_widget(self.info)

      self.instructions1 = Label(text = "Press enter to make another flower! Click on the center of a flower to pause it.", pos=(500, 500), text_size=(800,100), valign='top', markup=True)

      self.add_widget(self.instructions1)

      self.flowers = []
      self.key = 60 + 5*len(self.flowers) #pitch of current key

      color = (np.random.rand(),np.random.rand(), np.random.rand(), 1)
      flower = Flower((200, 300), 8, 100, color, self.key)
      flower.button.bind(on_press = lambda x: self.pause_generator(flower))
      self.add_widget(flower.button)

      self.canvas.add(flower)
      self.flowers.append(flower)

      self.add_flower_mode = False

      self.audio = Audio()
      self.on_update()

      self.pos = [0,0]
   
   def on_key_down(self, keycode, modifiers):
      if keycode[1] == "enter":
         if len(self.flowers) < 10:
            color = (np.random.rand(),np.random.rand(), np.random.rand(), 1)
            flower = Flower((Window.mouse_pos[0], Window.mouse_pos[1]), 8, 100, color, self.key)
            flower.button.bind(on_press = lambda x: self.pause_generator(flower))
            self.add_widget(flower.button)

            self.canvas.add(flower)
            self.flowers.append(flower)
      
      elif keycode[1] in waveform_dict:
            for flower in self.flowers:
               for petal in flower.petals:
                  flower.petals[petal][0]  = waveform_dict[keycode[1]]

   
   def on_key_up(self, keycode):
      if keycode[1] == "enter":
         self.add_flower_mode = False 


   def pause_generator(self, flower):
      flower.active = not flower.active
      if not flower.active:
         for petal_angle in flower.petals:
               notecontents = flower.petals[petal_angle][0]
               note = NoteGenerator(notecontents[0], notecontents[1], notecontents[2], notecontents[3])
               self.audio.remove_generator(note)
      return True

   def on_update(self):
      self.info.text = str(Window.mouse_pos)
      self.info.text += '\nfps:%d' % kivyClock.get_fps()
      
      for flower in self.flowers:
         flower.on_update(kivyClock.frametime, 0.2)
         for petal in flower.petals:
            if int(flower.rotate.angle) % 360 == petal % 360:
               if flower.active:
                  print "help!"
                  notecontents = flower.petals[petal][0]
                  note = NoteGenerator(notecontents[0], notecontents[1], notecontents[2], type = notecontents[3])
                  self.audio.add_generator(note) 
                  flower.petals[petal][1].a = 1.0
 

######################################################################################################


run(MainWidget5)


