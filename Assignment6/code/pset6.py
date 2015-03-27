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

color_dict = {
         0: (255,0,0),
         1: (255,128,0),
         2: (255,255,0),
         3: (102,255,102),
         4: (0,255,128),
         5: (0,255,0),
         6: (255,0,255),
         7: (0,0,255),
         8: (154,-64,-143),
         9: (127,0,255),
         10: (255,51,255),
         11: (255,51,153)
      }

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
   def __init__(self, bottom_pt, top_pt, rgb, pitch):
      super(String, self).__init__()
      self.bottom_pt = bottom_pt
      self.top_pt = top_pt
      self.pitch = pitch
      self.width = self.calc_width()
      self.mid_pt = (bottom_pt[0], (top_pt[1] - bottom_pt[1])/2 + bottom_pt[1])
      self.string = Line(points = [self.top_pt[0], self.top_pt[1], self.mid_pt[0], self.mid_pt[1], self.bottom_pt[0], self.bottom_pt[1]], width = self.width)
      self.active = True
      self.color = Color(*rgb)
      self.add(self.color)

   # bends the string by moving the mid-point of the string to the "hand
   # location
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
      self.string = Line(points = [self.top_pt[0], self.top_pt[1], self.mid_pt[0], self.mid_pt[1], self.bottom_pt[0], self.bottom_pt[1]], width = self.width)
      #self.add(self.color)
      self.add(self.string)
      return self

   def inc_half_step(self):
      self.pitch = self.pitch + 1
      self.width = self.calc_width()
      self.remove(self.color)
      self.color = Color(*color_dict[self.pitch % 12])

   def dec_half_step(self):
      self.pitch = self.pitch - 1
      self.width = self.calc_width()
      self.remove(self.color)
      self.color = Color(*color_dict[self.pitch % 12])

   def calc_width(self):
      return abs(10 - self.pitch/10)

#This class attempts to figure out if the user is waving their hand
# from the top of the screen to the bottom of the screen or visa versa
# within a few seconds
class WaveGesture(object):
   def __init__(self, harp, song):
      super(WaveGesture, self).__init__()
      self.harp = harp
      self.song = song
      self.top = harp.area[1] + harp.pos[1]
      self.pixel_thresh = 100
      self.tick_thresh = 480
      self.bottom = harp.pos[1]
      self.middle = (self.top - self.bottom)/2 + self.bottom
      self.previous_motions = []
      self.at_top = (False, 0)
      self.at_bottom = (False, 0)
      self.at_middle = (False, 0)
      self.activated = (False, 0)

   def set_hand_pos(self, x, y, active):
      tick = self.song.cond.get_tick()
      
      if self.activated[0] == True and self.activated[1] + self.tick_thresh < tick:
         self.activated = (False, tick)
      if active:
         if x > 700:
            if y > self.top - self.pixel_thresh:
               self.at_top = (True, tick)
               print "top tick: " + str(self.at_top)
            elif y < self.middle + self.pixel_thresh/2 and y > self.middle - self.pixel_thresh/2:
               self.at_middle = (True, tick)
            elif y < self.bottom + self.pixel_thresh:
               self.at_bottom = (True, tick)
               print " bottom tick: " + str(self.at_bottom)

   def detect_wave(self):
      tick = self.song.cond.get_tick()
      if self.activated[0] == False and self.at_middle[0] and (self.at_top[0] or self.at_bottom[0]):
         print "top tick: " + str(self.at_top) + " bottom tick: " + str(self.at_bottom)
         if abs(self.at_top[1] - self.at_middle[1]) < self.tick_thresh or abs(self.at_bottom[1] - self.at_middle[1]) < self.tick_thresh:
            #If top occured more recently than bottom, wave went up
            self.activated = (True, tick)
            if self.at_top[1] - self.at_middle[1] > 0:
               return "up"
            elif self.at_bottom[1] - self.at_middle[1] > 0:
               return "down"

      
# This class monitors the location of the hand and determines if a pluck of
# the string happened. Each PluckGesture is associated with a string (1-1
# correspondence). The PluckGesture also controls controls the String instance by 
# setting its behavior
class PluckGesture(object):
   def __init__(self, harp, string, grab_thresh, pluck_thresh):
      super(PluckGesture, self).__init__()
      self.harp = harp
      self.string = string
      self.grab_thresh = grab_thresh
      self.pluck_thresh = pluck_thresh
      self.grabbed = False

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
         self.harp.on_pluck(self.string.pitch)
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
      self.song.start()
      
      self.active = False
      self.active_color = (0,255,0)
      self.inactive_color = (255, 0, 0)
      
      self.synth = synth
      self.synth.program(0, 46, 0)
      self.noteplayer = NotePlayer(self.synth, self.song)

      self.major_scale = [60, 62, 64, 65, 67, 69, 71, 72] 
 
      ###########
      # Strings
      ###########

      self.strings = []
      for i in range(self.num_strings):
         x = self.area[0] / self.num_strings * i + self.pos[0]
         pitch = self.major_scale[i%9]
         rgb = color_dict[pitch % 12]
         string = String((x, pos[1]), (x, area[1] + pos[1]), rgb, pitch)

         self.strings.append(string)


      ###############
      # PluckGestures
      ###############

      self.pluckgestures = []
      for i in range(self.num_strings):
         pluckgesture = PluckGesture(self, self.strings[i], 50, 100)
         self.pluckgestures.append(pluckgesture)


      #################
      # Wave Gesture
      #################
      self.wavegesture = WaveGesture(self, self.song)


   # set the hand position as a 3D vector ranging from [0,0,0] to [1,1,1]
   def set_hand_pos(self, pos):
      self.cursor.set_pos(pos)
      self.z_index = pos[2]
      self.active = True if self.z_index >= .2 else False
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
      self.harp = Harp(self.synth, area, pos, 8) #harp initalization, 10 strings
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

      ##############
      # Wave Gesture
      ##############
      
      self.harp.wavegesture.set_hand_pos(pt[0], pt[1], self.harp.active)
      wavedir = self.harp.wavegesture.detect_wave()
      if wavedir == "up":
         for pluckgesture in self.harp.pluckgestures:
            pluckgesture.string.inc_half_step()
      elif wavedir == "down":
         for pluckgesture in self.harp.pluckgestures:
            pluckgesture.string.dec_half_step()
      
      for pluckgesture in self.harp.pluckgestures:
         pluckgesture.set_hand_pos(pt[0],pt[1], self.harp.active)
         pluckgesture.string.on_update()

   def on_key_down(self, keycode, modifiers):
      if kUseKinect == False:
         if keycode[1] == "up":
            for pluckgesture in self.harp.pluckgestures:
               pluckgesture.string.inc_half_step()

         if keycode[1] == "down":
             for pluckgesture in self.harp.pluckgestures:
               pluckgesture.string.dec_half_step()
      
# convert pt into unit scale (ie, range [0,1]) assuming that pt falls in the
# the range [min_val, max_val]
# value is clipped [0,1]
def scale_point(pt, min_val, max_val):
   pt = (pt - np.array(min_val)) / (np.array(max_val) - np.array(min_val))
   pt = np.clip(pt, 0, 1)
   return pt


# pass in which MainWidget to run as a command-line arg
run(MainWidget)
