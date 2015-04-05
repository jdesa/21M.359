#pset7.py


import sys
sys.path.append('./common')
from core import *
from audio import *
from clock import *
from song import *
from audiotrack import *
from wavegen import *
from graphics import *

from kivy.uix.label import Label
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock
from kivy.uix.button import Button

import random
import numpy as np
import bisect
from collections import namedtuple


color_dict = [(255,0,0),
         (255,128,0),
         (255,255,0),
         (255,20,147),
         (0,255,128),
         (0,255,0),
         (255,0,255),
         (0,0,255),
         (138,43,226),
         (127,0,255),
         (255,51,255),
         (255,51,153)
      ]

class CornerRectangleWidget(Widget):
    def __init__(self, **kwargs):
        super(CornerRectangleWidget, self).__init__(**kwargs)

        with self.canvas:
            Color(1, 0, 0, 1)  # set the colour to red
            self.rect = Rectangle(pos=self.center,
                                  size=(self.width/2.,
                                        self.height/2.))

        self.bind(pos=self.update_rect,
                  size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.test = CornerRectangleWidget()
      #self.add_widget(self.test)
      
      self.gemdata = GemData("examplegemfile.txt");
      self.audiocontroller = AudioController("bwww", "TakeMeOut")
      
      self.beatmatchdisplay = BeatMatchDisplay(self.gemdata, "")
      self.canvas.add(self.beatmatchdisplay)

   def on_key_down(self, keycode, modifiers):
      # play / stop toggle
      if keycode[1] == 'p':
         self.audiocontroller.toggle()
      if keycode[1] == 't':
         print(self.gemdata.get_all_ticks())
      if keycode[1] == 'spacebar':
         self.audiocontroller.set_mute(True)

      # button down   
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass

   def on_key_up(self, keycode):
      # button up
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass

   def on_update(self) :
      pass

# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
   def __init__(self, sfx_name, song_name):
      super(AudioController, self).__init__()
      self.audio = Audio()
      self.sfx_name = sfx_name
      self.song_name = song_name

      self.song = Song()
      #add background track
      self.bg_track = AudioTrack(self.audio, self.song_name + "_bg.wav")
      self.song.add_track(self.bg_track)

      #add solo track
      self.solo_track = AudioTrack(self.audio, self.song_name + "_solo.wav")
      self.song.add_track(self.solo_track)

   # start / stop the song
   def toggle(self):
      self.song.toggle()

   # get the conductor
   def get_cond(self):
      return self.song.cond

   # mute / unmute the solo track
   def set_mute(self, mute):
      self.solo_track.set_mute(mute)

   # play a sound-fx (miss sound)
   def play_sfx(self):
      pass

   # needed to update song
   def on_update(self):
      pass

kticksperquarter = 480
class Gem(object):
   def __init__(self, tick, track, duration):
      super(Gem, self).__init__()
      self.tick = tick
      self.track = track
      self.duration = duration

   def __repr__(self):
      return "Tick: " + str(self.tick) + " Track: " + str(self.track) + " Duration: " + str(self.duration)

# holds data for gems
class GemData(object):
   def __init__(self, filepath):
      super(GemData, self).__init__()
      self.gems = []
      self.ticks = []  # list of just the ticks - for fast lookup by tick if using bisect
      self.read_gem_data(filepath)
      self.tracks = 0

   # read gem data from file
   # starting number = gen's lane
   # period = rest
   def read_gem_data(self, filepath):
      f = open(filepath)
      tick = 0
      max_track = 0
      for line in iter(f):
         colon_split = line.split(":")         
         rhythm_type = int(colon_split[0]);
         gemstring = colon_split[1]
         for i in range(len(gemstring)): 
            track = gemstring[i]
            duration = kticksperquarter / rhythm_type
            if track in ["1","2","3", "4", "5"]:
               track = int(track)
               if track > max_track:
                  max_track = track
               gem = Gem(tick, track, duration)
               self.gems.append(gem)
               self.ticks.append(tick)
            tick += duration

   def get_all_gems(self):
      return self.gems

   def get_all_ticks(self):
      return self.ticks

   # return a sublist of the gems that match this time slice:
   def get_gems_in_range(self, start_tick, end_tick):
      pass

   def get_len(self):
      return len(self.gems)



# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
   def __init__(self, pos, color):
      super(GemDisplay, self).__init__()
      self.color = color
      self.color.a = .1
      self.pos = pos
      self.rectangle = Rectangle(pos=(pos+pos/2, pos+pos/2), size=(100, 100))

   # change to display this gem being hit
   def on_hit(self):
      self.color.a = 1

   # change to display a passed gem
   def on_pass(self):
      self.color = .1

   # useful if gem is to animate
   def on_update(self, dt):
      pass

# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
   def __init__(self, pos, color):
      super(ButtonDisplay, self).__init__()
      self.color = Color(*color)
      self.color.a = .75
      self.pos = pos
      self.rectangle = Rectangle(pos=(pos, 0), size=(width/5, 50))
      self.add(self.rectangle)
   # displays when button is down (and if it hit a gem)
   def on_down(self, hit):
      if hit:
         print "Hit a gem!"
      else:
         print "Did not hit a gem."

   # back to normal state
   def on_up(self):
      print "Button on up" 

width = 800
height = 600
# Displays all game elements: Nowbar, Buttons, BarLines, Gems.
# scrolls the gem display.
# controls the gems and nowbar buttons
class BeatMatchDisplay(InstructionGroup):
   def __init__(self, gem_data, cond):
      super(BeatMatchDisplay, self).__init__()
      self.gem_data = gem_data
      self.cond = cond

      #Button Creation
      self.nowbar = []
      for i in range(5):
         button = ButtonDisplay(i*width/5,color_dict[i+2])
         self.nowbar.append(button)
         self.add(button.color)
         self.add(button)
      print self.nowbar

   # called by Player. Causes the right thing to happen
   def gem_hit(self, gem_idx):
      pass

   # called by Player. Causes the right thing to happen
   def gem_pass(self, gem_idx):
      pass

   # called by Player. Causes the right thing to happen
   def on_button_down(self, lane, hit):
      pass

   # called by Player. Causes the right thing to happen
   def on_button_up(self, lane):
      pass

   # call every frame to make gems and barlines flow down the screen
   def on_update(self) :
      pass



# Handles game logic and keeps score. 
# Controls the display and the audio
class Player(object):
   def __init__(self, gem_data, display, audio_ctrl):
      super(Player, self).__init__()

   # called by MainWidget
   def on_button_down(self, lane) :
      pass

   # called by MainWidget
   def on_button_up(self, lane):
      pass

   # needed to check if for pass gems (ie, went past the slop window)
   def on_update(self) :
      pass

run(MainWidget)
