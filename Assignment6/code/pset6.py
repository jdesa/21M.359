#Kinect Harp

# common import
import sys
sys.path.append('./common')
from core import *
from kinect import *
from graphics import *
from song import *
from clock import *
from clock import kTicksPerQuarter
from audio import *
from synth import *

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup

import numpy as np


# This class is a simple note player that knows how to play a note on and will
# automatically call the note off some time later. Remeber to call on_update()
# on it.
class NotePlayer(object):
   def __init__(self, synth, song):
      super(NotePlayer, self).__init__()
      self.synth = synth
      self.song = song
      self.beat_len = kTicksPerQuarter
      self.channel = 0

   def play_note(self, pitch, velocity, duration):
      self.synth.noteon(self.channel, pitch, duration)
      tick = self.song.cond.get_tick()
      self.song.sched.post_at_tick(tick + duration, self.synth.noteoff(self.channel, pitch), pitch)

   def on_update(self):
      pass

# This class displays a single string on screen. It knows how to draw the
# string and how to bend it by setting the mid-point of the line
class String(InstructionGroup):
   def __init__(self, bottom_pt, top_pt, rgb):
      super(String, self).__init__()
      self.bottom_pt = bottom_pt
      self.top_pt = top_pt
      self.mid_pt = (bottom_pt[0], (top_pt[1] - bottom_pt[1])/2 + bottom_pt[1])
      self.string = Line(points = [self.top_pt[0], self.top_pt[1], self.mid_pt[0], self.mid_pt[1], self.bottom_pt[0], self.bottom_pt[1]], width = 5)
      self.active = True
      self.color = Color(*rgb)
      self.add(self.color)
   # bends the string by moving the mid-point of the string to the "hand
   # location"
   def set_mid_point(self, x, y):
      if self.active:
         self.mid_pt = (x,y)

   def get_mid_point(self):
      return self.mid_pt

   # resets the string to being normal / still.
   def set_inactive(self):
      self.active = False

   # useful for the gesture to know what the resting x-position of the string
   # is
   def get_resting_x(self):
      return self.top_pt[0]

   def get_mid_point_height(self):
      return (self.top_pt[1] - self.bottom_pt[1])/2 + self.bottom_pt[1]

   # if the string is going to animate (say, when it is plucked), on_update is
   # necessary
   def on_update(self):
      self.remove(self.string)
      self.string = Line(points = [self.top_pt[0], self.top_pt[1], self.mid_pt[0], self.mid_pt[1], self.bottom_pt[0], self.bottom_pt[1]], width = 5)
      self.add(self.string)
      return self

# This class monitors the location of the hand and determines if a pluck of
# the string happened. Each PluckGesture is associated with a string (1-1
# correspondence). The PluckGesture also controls controls the String instance by 
# setting its behavior
class PluckGesture(object):
   def __init__(self, harp, string, grab_thresh, pluck_thresh, pitch):
      super(PluckGesture, self).__init__()
      self.harp = harp
      self.string = string
      self.grab_thresh = grab_thresh
      self.pluck_thresh = pluck_thresh
      self.grabbed = False
      self.pitch = pitch

   def set_hand_pos(self, x, y, active):
      if not self.harp.active:
         self.grabbed = False
         #print "inactive"

      elif self.harp.active and abs(x - self.string.get_resting_x()) < 50:
         self.grabbed = True
         self.string.set_mid_point(x, y)
         #print "grabbed"

      elif self.grabbed and self.harp.active and abs(x - self.string.get_resting_x()) >= 50 and abs(x - self.string.get_resting_x()) < 100:
         self.grabbed = False
         self.string.set_mid_point(self.string.get_resting_x(), self.string.get_mid_point_height())
         self.harp.on_pluck(self.pitch)
         #print "plucked"

      else:
         self.grabbed = False
         self.string.set_mid_point(self.string.get_resting_x(), self.string.get_mid_point_height())
         #print "neither"


# The Harp class combines the above classes into a fully working harp. It
# instantiates the strings and pluck gestures as well as a hand cursor display
class Harp(InstructionGroup):
   def __init__(self, synth, area, pos, num_strings):
      super(Harp, self).__init__()
      self.area = area
      self.pos = pos
      self.num_strings = num_strings
      self.cursor = Cursor3D(area, pos, (.2, .6, .2), True)
      self.z_index = 0
      self.song = Song()
      
      self.active = False
      self.active_color = (0,255,0)
      self.inactive_color = (255, 0, 0)
      
      self.synth = synth
      self.synth.program(0, 46, 0)
      self.noteplayer = NotePlayer(self.synth, self.song)

 
      ###########
      # Strings
      ###########

      self.strings = []
      for i in range(self.num_strings):
         x = self.area[0] / self.num_strings * i + self.pos[0]
         if i % 7 == 0: 
            rgb = (255,0,0)
         elif i % 7 == 3:
            rgb = (0,0,255)
         else:
            rgb = (255,255,255)
         string = String((x, pos[1]), (x, area[1] + pos[1]), rgb)

         self.strings.append(string)


      ###############
      # PluckGestures
      ###############

      self.pluckgestures = []
      for string in self.strings:
         pluckgesture = PluckGesture(self, string, 50, 100, 60)
         self.pluckgestures.append(pluckgesture)


   # set the hand position as a 3D vector ranging from [0,0,0] to [1,1,1]
   def set_hand_pos(self, pos):
      self.cursor.set_pos(pos)
      self.z_index = pos[2]
      self.active = True if self.z_index <= .5 else False
      color = self.active_color if self.active else self.inactive_color
      self.cursor.set_color(color)


   # callback to be called from a PluckGesture when a pluck happens
   def on_pluck(self, pitch):
      self.noteplayer.play_note(pitch,100,100)
      print "plucked"

   # for animation and NotePlayer
   def on_update(self, dt):
      pass

kUseKinect = False

# add the scene that will display the hand position
# find reasonable min/max for hand position (hard-coded) and display
# show depth as size of circle
class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()

      # and text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      if kUseKinect:
         self.kinect = Kinect()
         self.kinect.add_joint(kJointRightHand)

      self.grabbed = False
      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      ############
      # Harp
      ############
      area = (600, 400) #harp area
      pos = (100, 100) #Harp position
      self.harp = Harp(self.synth, area, pos, 7) #harp initalization, 10 strings
      self.canvas.add(self.harp)
     
      self.canvas.add(Color(255,255,255))
      self.canvas.add(self.harp.cursor)

      for pluckgesture in self.harp.pluckgestures:
         self.canvas.add(pluckgesture.string)
         print "pluckgesture.string: " + str(pluckgesture.string)


   def on_update(self) :
      if kUseKinect:
         # NOTE: the scaling parameters are just placeholder and can be changed as needed.
         self.kinect.on_update()
         pt = self.kinect.get_joint(kJointRightHand)
         pt_min = np.array([-250.0, -200, 0])
         pt_max = np.array([700.0, 700, -500])
         norm_pt = scale_point(pt, pt_min, pt_max)

      else:
         pt = [Window.mouse_pos[0], Window.mouse_pos[1], 0.5]
         if 'shift' in self.down_keys:
            pt[2] = 0.5

         pt_min = np.array([0., 0., 0.])
         pt_max = np.array([800., 600., 1.])
         norm_pt = scale_point(pt, pt_min, pt_max)


      self.label.text = '\n'.join(['%.0f %.2f' % x for x in zip(pt, norm_pt)])
      
      self.harp.set_hand_pos(norm_pt)
      
      for pluckgesture in self.harp.pluckgestures:
         pluckgesture.set_hand_pos(pt[0],pt[1], self.harp.active)
         pluckgesture.string.on_update()
         print "string: " + str(pluckgesture.string)
         print "string info: " + str(pluckgesture.string.get_mid_point())

      '''
      for string in self.harp.strings:
         string.on_update()
         print "string: " + str(string)
         print "canvas: " + str(self.canvas)
      '''
      print " load: " + str(self.audio.get_load())
      
# convert pt into unit scale (ie, range [0,1]) assuming that pt falls in the
# the range [min_val, max_val]
# value is clipped [0,1]
def scale_point(pt, min_val, max_val):
   pt = (pt - np.array(min_val)) / (np.array(max_val) - np.array(min_val))
   pt = np.clip(pt, 0, 1)
   return pt


# pass in which MainWidget to run as a command-line arg
run(MainWidget)
