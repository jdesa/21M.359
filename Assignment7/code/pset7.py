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


color_dict = [
         (0,128,0),
         (128,0,0),
         (0,128,128),
         (128,0,128),
         (0,0,128)
      ]
width = 800
height = 600
numtracks = 5
gem_height = 50
track_width = width/numtracks

class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()   
      self.audiocontroller = AudioController("bwww", "TakeMeOut")
      
      self.gemdata = GemData("examplegemfile.txt");
      self.beatmatchdisplay = BeatMatchDisplay(self.gemdata, self.audiocontroller.song.cond)
      self.canvas.add(self.beatmatchdisplay)

   def on_key_down(self, keycode, modifiers):
      # play / stop toggle
      if keycode[1] == 'p':
         self.audiocontroller.toggle()

      if keycode[1] == 't':
         #print(self.gemdata.get_all_ticks())
         pass
      if keycode[1] == 'spacebar':
         self.audiocontroller.set_mute(True)

      if keycode[1] == "a":
         self.beatmatchdisplay.nowbar[0].on_down(True)
      if keycode[1] == "s":
         self.beatmatchdisplay.nowbar[1].on_down(True)
      if keycode[1] == "d":
         self.beatmatchdisplay.nowbar[2].on_down(True)
      if keycode[1] == "f":
         self.beatmatchdisplay.nowbar[3].on_down(True)
      if keycode[1] == "g":
         self.beatmatchdisplay.nowbar[4].on_down(True)

      # button down   
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass

   def on_key_up(self, keycode):
      # button up
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass
      if keycode[1] == "a":
         self.beatmatchdisplay.nowbar[0].on_up()
      if keycode[1] == "s":
         self.beatmatchdisplay.nowbar[1].on_up()
      if keycode[1] == "d":
         self.beatmatchdisplay.nowbar[2].on_up()
      if keycode[1] == "f":
         self.beatmatchdisplay.nowbar[3].on_up()
      if keycode[1] == "g":
         self.beatmatchdisplay.nowbar[4].on_up()

   def on_update(self) :
      self.beatmatchdisplay.on_update()

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
      # set up Tempo Track correctly.
      self.tempo_map = TempoMap("_takemeout_tempo.txt")
      self.song.cond.set_tempo_map(self.tempo_map)
      print (str(self.song.cond.tempo_map))
      
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
      self.song.on_update()

kticksperquarter = 480
class Gem(object):
   def __init__(self, tick, track, duration):
      super(Gem, self).__init__()
      self.tick = tick
      self.track = track
      self.duration = duration

   def __repr__(self):
      return "Tick: " + str(self.tick) + " Track: " + str(self.track) + " Duration: " + str(self.duration)

   def track_to_posx(self):
      return self.track*track_width

   def tick_to_posy(self):
      return self.tick

   def get_tick(self):
      return self.tick

class BarLineDisplay(InstructionGroup):
   def __init__(self, tick):
      super(BarLineDisplay, self).__init__()
      self.tick = tick
      self.line = Rectangle(pos=(0, tick), size=(800, 1))
      self.add(Color(255,255,255))
      self.add(self.line)

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
         if line in ['\n', '\r\n']:
            pass
         else:
            colon_split = line.split(":")   
            rhythm_type = int(colon_split[0]);
            gemstring = colon_split[1]
            for i in range(len(gemstring)): 
               track = gemstring[i]
               duration = kticksperquarter / rhythm_type
               if track == ".":
                  tick += duration
               elif track in ["0", "1","2","3", "4"]:
                  track = int(track)
                  if track > max_track:
                     max_track = track
                  gem = Gem(tick, track, duration)
                  self.gems.append(gem)
                  self.ticks.append(tick)
                  tick += duration
               #print "tick is: " + str(tick)

   def get_all_gems(self):
      return self.gems

   def get_all_ticks(self):
      return self.ticks

   # return a sublist of the gems that match this time slice:
   def get_gems_in_range(self, start_tick, end_tick):
      gems_in_range = [x for x in self.gems if (start_tick <= x and x <= end_tick)]
      return gems_in_range

   def get_len(self):
      return len(self.gems)

# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
   def __init__(self, pos, color):
      super(GemDisplay, self).__init__()
      self.color = Color(*color)
      self.color.a = .75
      self.pos = pos
      self.rectangle = Rectangle(pos=pos, size=(track_width, gem_height))
      self.add(self.color)
      self.add(self.rectangle)

   # change to display this gem being hit
   def on_hit(self):
      self.color.a = 1

   # change to display a passed gem
   def on_pass(self):
      self.color = .5

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
      self.rectangle = Rectangle(pos=(pos, 0), size=(track_width, gem_height))
      self.add(self.color)
      self.add(self.rectangle)
   # displays when button is down (and if it hit a gem)
   def on_down(self, hit):
      self.color.a = 1
      if hit:
         print "Hit a gem."
      else:
         print "Did not hit a gem."

   # back to normal state
   def on_up(self):
      self.color.a = .75
      print "Button on up" 

# Displays all game elements: Nowbar, Buttons, BarLines, Gems.
# scrolls the gem display.
# controls the gems and nowbar buttons
class BeatMatchDisplay(InstructionGroup):
   def __init__(self, gem_data, cond):
      super(BeatMatchDisplay, self).__init__()
      self.cond = cond

      #Button Creation
      self.nowbar = []
      for i in range(5):
         button = ButtonDisplay(i*track_width,color_dict[i])
         self.nowbar.append(button)
         self.add(button)

      self.translate = Translate(0,0)
      print "translate: " + str(self.translate)
      self.add(self.translate)

      #Gem Creation
      self.gem_data = gem_data

      #Barline Creation
      max_tick  = self.gem_data.get_all_gems()[-1].get_tick()
      print "max_tick is: " + str(max_tick)
      for tick in range(0, max_tick, kticksperquarter):
         bar = BarLineDisplay(tick - kticksperquarter/2)
         self.add(bar)

      for gem in self.gem_data.get_all_gems():
         pos = (gem.track_to_posx(), gem.tick_to_posy())
         color = color_dict[gem.track]
         gemdisplay = GemDisplay(pos, color)
         self.add(gemdisplay)
      


   # called by Player. Causes theright thing to happen
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
      self.translate.y = - (self.cond.get_tick()/4.0)

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
