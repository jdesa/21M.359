#Kinect Harp

# common import
import sys
sys.path.append('./common')
from core import *
from kinect import *
from graphics import *

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup

import numpy as np


# This class is a simple note player that knows how to play a note on and will
# automatically call the note off some time later. Remeber to call on_update()
# on it.
class NotePlayer(object):
   def __init__(self, synth):
      super(NotePlayer, self).__init__()
      self.synth = synth

   def play_note(self, pitch, velocity, duration):
      pass

   def on_update(self):
      pass

# This class displays a single string on screen. It knows how to draw the
# string and how to bend it by setting the mid-point of the line
class String(InstructionGroup):
   def __init__(self, bottom_pt, top_pt, rgb):
      super(String, self).__init__()


   # bends the string by moving the mid-point of the string to the "hand
   # location"
   def set_mid_point(self, x, y):
      pass

   # resets the string to being normal / still.
   def set_inactive(self):
      pass

   # useful for the gesture to know what the resting x-position of the string
   # is
   def get_resting_x(self):
      return 0

   # if the string is going to animate (say, when it is plucked), on_update is
   # necessary
   def on_update(self, dt):
      pass


# This class monitors the location of the hand and determines if a pluck of
# the string happened. Each PluckGesture is associated with a string (1-1
# correspondence). The PluckGesture also controls controls the String instance by 
# setting its behavior
class PluckGesture(object):
   def __init__(self, string, grab_thresh, pluck_thresh, idx, callback):
      super(PluckGesture, self).__init__()

   def set_hand_pos(self, x, y, active):
      pass


# The Harp class combines the above classes into a fully working harp. It
# instantiates the strings and pluck gestures as well as a hand cursor display
class Harp(InstructionGroup):
   def __init__(self, area, pos, num_strings):
      super(Harp, self).__init__()
      self.area = area
      self.pos = pos
      self.num_strings = num_strings
      self.cursor = Cursor3D(area, pos, (.2, .6, .2), True)


   # set the hand position as a 3D vector ranging from [0,0,0] to [1,1,1]
   def set_hand_pos(self, pos):
      self.cursor.set_pos(pos)


   # callback to be called from a PluckGesture when a pluck happens
   def on_pluck(self, idx):
      print 'pluck:', idx

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

      area = (600, 400) #harp area
      pos = (100, 100) #Harp position
      self.harp = Harp(area, pos, 10) #harp initalization, 10 strings
      self.canvas.add(self.harp)
      self.canvas.add(self.harp.cursor)

   def on_update(self) :
      if kUseKinect:
         # NOTE: the scaling parameters are just placeholder and can be changed as needed.
         self.kinect.on_update()
         pt = self.kinect.get_joint(kJointRightHand)
         pt_min = np.array([-250.0, -200, 0])
         pt_max = np.array([700.0, 700, -500])
         norm_pt = scale_point(pt, pt_min, pt_max)

      else:
         pt = [Window.mouse_pos[0], Window.mouse_pos[1], 0]
         if 'shift' in self.down_keys:
            pt[2] = 0.5

         pt_min = np.array([0., 0., 0.])
         pt_max = np.array([800., 600., 1.])
         norm_pt = scale_point(pt, pt_min, pt_max)


      self.label.text = '\n'.join(['%.0f %.2f' % x for x in zip(pt, norm_pt)])
      
      self.harp.set_hand_pos(norm_pt)




# convert pt into unit scale (ie, range [0,1]) assuming that pt falls in the
# the range [min_val, max_val]
# value is clipped [0,1]
def scale_point(pt, min_val, max_val):
   pt = (pt - np.array(min_val)) / (np.array(max_val) - np.array(min_val))
   pt = np.clip(pt, 0, 1)
   return pt


# pass in which MainWidget to run as a command-line arg
run(MainWidget)
