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

      self.player = Player(self.gemdata, self.beatmatchdisplay, self.audiocontroller)

   def on_key_down(self, keycode, modifiers):
      # play / stop toggle
      if keycode[1] == 'p':
         self.audiocontroller.toggle()

      if keycode[1] == 't':
         ###print(self.gemdata.get_all_ticks())
         pass
      if keycode[1] == 'spacebar':
         self.audiocontroller.set_mute(True)

      if keycode[1] == "a" or keycode[1] == "1":
         self.player.on_button_down(0)
      if keycode[1] == "s" or keycode[1] == "2":
         self.player.on_button_down(1)
      if keycode[1] == "d" or keycode[1] == "3":
         self.player.on_button_down(2)
      if keycode[1] == "f" or keycode[1] == "4":
         self.player.on_button_down(3)
      if keycode[1] == "g" or keycode[1] == "5":
         self.player.on_button_down(4)

      # button down   
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass

   def on_key_up(self, keycode):
      # button up
      idx = '12345'.find(keycode[1])
      if idx != -1:
         pass
      if keycode[1] == "a" or keycode[1] == "1":
         self.player.on_button_up(0)
      if keycode[1] == "s" or keycode[1] == "2":
         self.player.on_button_up(1)
      if keycode[1] == "d" or keycode[1] == "3":
         self.player.on_button_up(2)
      if keycode[1] == "f" or keycode[1] == "4":
         self.player.on_button_up(3)
      if keycode[1] == "g" or keycode[1] == "5":
         self.player.on_button_up(4)

   def on_update(self) :
      self.player.on_update()
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
      ####print(str(self.song.cond.tempo_map))
      
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
      self.line = Rectangle(pos=(0, tick + gem_height/2), size=(800, 1))
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
               ####print"tick is: " + str(tick)

   def get_all_gems(self):
      return self.gems

   def get_all_ticks(self):
      return self.ticks

   # return a sublist of the gems that match this time slice:
   def get_gems_in_range(self, start_tick, end_tick):
      gems_in_range = []
      for gem in self.gems:
         gem_tick = gem.get_tick()
         if start_tick <= gem_tick and gem_tick <= end_tick:
            gems_in_range.append(gem)
      return gems_in_range

   def get_gems_in_range_on_track(self, start_tick, end_tick, track):
      gems_in_range = []
      for gem in self.gems:
         gem_tick = gem.get_tick()
         if start_tick <= gem_tick and gem_tick <= end_tick and gem.track == track:
            gems_in_range.append(gem)
      return gems_in_range      

   def get_len(self):
      return len(self.gems)

# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
   def __init__(self, pos, color):
      super(GemDisplay, self).__init__()
      self.color = Color(*color)
      self.color.a = .5
      self.pos = pos
      self.rectangle = Rectangle(pos=pos, size=(track_width, gem_height))
      self.triggered = False
      self.added_to_canvas = False
      self.add(self.color)
      self.add(self.rectangle)


   # change to display this gem being hit
   def on_hit(self):
      self.color.a = 1
      self.triggered = True

   # change to display a passed gem
   def on_pass(self):
      ###print"hasn't been hit"
      ##print "gemdisplay hasn't been hit"
      self.color.rgb = (.5,.5,.5)
      self.color.a = .5
      self.triggered = True


   def has_triggered(self):
      return self.triggered

   # useful if gem is to animate
   def on_update(self, dt):
      pass

   def add_to_canvas(self):
      if not (self.added_to_canvas):
         #print "in add_to_canvas"
         self.add(self.color)
         self.add(self.rectangle)
         self.added_to_canvas = True

   def remove_from_canvas(self):
      if (self.added_to_canvas):
         print "in remove_from_canvas"
         self.remove(self.color)
         self.remove(self.rectangle)
         self.added_to_canvas = False

# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
   def __init__(self, pos, color):
      super(ButtonDisplay, self).__init__()
      self.rgb = color
      self.color = Color(*color)
      self.color.a = .5
      self.pos = pos
      self.rectangle = Rectangle(pos=(pos, 100), size=(track_width, gem_height))
      self.add(self.color)
      self.add(self.rectangle)

   # displays when button is down (and if it hit a gem)
   
   def on_button_down(self):
      self.color.a = 1
      self.color.rgb = self.rgb


   def on_down(self, hit):
      if hit:
         self.color.rgb = (1,1,1)
         self.color.a = 1
         ####print"Hit a gem."
      else:
         self.color.rgb = (.5,.5,.5)
         self.color.a = .5
         ####print"Did not hit a gem."

   # back to normal state
   def on_up(self):
      #print "on_up being called"
      self.color.rgb = self.rgb
      self.color.a = .5
      ####print"Button on up"  

# Displays all game elements: Nowbar, Buttons, BarLines, Gems.
# scrolls the gem display.
# controls the gems and nowbar buttons
class BeatMatchDisplay(InstructionGroup):
   def __init__(self, gem_data, cond):
      super(BeatMatchDisplay, self).__init__()
      self.cond = cond
      self.gem_data = gem_data

      #Button Creation
      self.nowbar = []
      for i in range(5):
         button = ButtonDisplay(i*track_width,color_dict[i])
         self.nowbar.append(button)
         self.add(button)

      self.translate = Translate(0,0)
      ###print"translate: " + str(self.translate)
      self.add(self.translate)

      #Gem Creation
      self.gem_data = gem_data

      #Barline Creation
      max_tick  = self.gem_data.get_all_gems()[-1].get_tick()
      ####print"max_tick is: " + str(max_tick)
      for tick in range(0, max_tick, kticksperquarter):
         bar = BarLineDisplay(tick - kticksperquarter/2)
         self.add(bar)

      self.gemdisplaydict = {}

      for gem in self.gem_data.get_all_gems():
         pos = (gem.track_to_posx(), gem.tick_to_posy())
         color = color_dict[gem.track]
         gemdisplay = GemDisplay(pos, color)
         self.gemdisplaydict[gem] = gemdisplay
         self.add(gemdisplay)
      
   # called by Player. Causes theright thing to happen
   def gem_hit(self, gem):
      ###print"in gem_hit!"
      self.gemdisplaydict[gem].on_hit()

   # called by Player. Causes the right thing to happen
   def gem_pass(self, gem):
      ###print"in gem_pass!"
      self.gemdisplaydict[gem].on_pass()
      self.nowbar[gem.track].on_down(False)

   # called by Player. Causes the right thing to happen
   def on_button_down(self, lane, hit):
      ###print"on_button_down from beatmatchdisplay"
      self.nowbar[lane].on_down(hit)

   # called by Player. Causes the right thing to happen
   def on_button_up(self, lane):
      self.nowbar[lane].on_up()

   # call every frame to make gems and barlines flow down the screen
   def on_update(self) :
      self.translate.y = - (self.cond.get_tick()/4.0)

   def draw_gems(self,drawable_gems):
      non_drawable_gems = []
      for gem in self.gem_data.get_all_gems():
         if gem not in drawable_gems:
            non_drawable_gems.append(gem)

      #print "non_drawable_gems: " + str(non_drawable_gems)
      
      for gem in drawable_gems:
         ##print "in beatmatchdisplay drawable_gems"
         self.gemdisplaydict[gem].add_to_canvas()

      for gem in non_drawable_gems:
         self.gemdisplaydict[gem].remove_from_canvas()

# Handles game logic and keeps score. 
# Controls the display and the audio
class Player(object):
   def __init__(self, gem_data, display, audio_ctrl):
      super(Player, self).__init__()
      self.gemdata = gem_data
      self.beatmatchdisplay = display
      self.audio_ctrl = audio_ctrl
      self.score = 0

   # called by MainWidget
   def on_button_down(self, lane) :
      #print "player on button down"

      self.beatmatchdisplay.nowbar[lane].on_button_down()


      current_tick = self.audio_ctrl.song.cond.get_tick()
      lower_tick_bound = (current_tick)/4 - 50 + 150
      upper_tick_bound = (current_tick)/4 + 50 + 150
      possible_gem_list = self.gemdata.get_gems_in_range_on_track(lower_tick_bound, upper_tick_bound, lane)      
      if len(possible_gem_list) == 0:
         pass
         ###print"lower_tick_bound: " + str(lower_tick_bound)
         ###print"upper_tick_bound: " + str(upper_tick_bound)
         ###print"lane: " + str(lane)
         ####printself.gemdata.get_all_gems()
      elif len(possible_gem_list) == 1:

         ###print"lower_tick_bound: " + str(lower_tick_bound)
         ###print"upper_tick_b ound: " + str(upper_tick_bound)
         ###print"lane: " + str(lane)
         ###print"hit gem"
         self.beatmatchdisplay.gem_hit(possible_gem_list[0])
      else:
         pass
         ###print"multiple gems in range"

   # called by MainWidget
   def on_button_up(self, lane):
      #print "player on button up"
      #self.button_up()
      self.beatmatchdisplay.on_button_up(lane)

   # needed to check if for pass gems (ie, went past the slop window)
   def on_update(self):
      ##print "in on_update"
      self.draw_gems()
      older_tick = self.audio_ctrl.song.cond.get_tick()
      ##print "older tick is: " + str(older_tick)
      lower_tick_bound = (older_tick)/4 - 50 + 50
      upper_tick_bound = (older_tick)/4 + 50 + 50
      possible_gem_list = []

      for lane in range(5):
         possible_gem_list += self.gemdata.get_gems_in_range_on_track(lower_tick_bound, upper_tick_bound, lane)      
         
      untouched_gems = []
      for gem in possible_gem_list:
         gemdisplay = self.beatmatchdisplay.gemdisplaydict[gem]
         ##print "gemdisplay_has_triggered():" + str(gemdisplay.has_triggered())
         if not(gemdisplay.has_triggered()):
            untouched_gems.append(gem)

      if len(untouched_gems) == 0:
         ##print"no hit gems"
         pass
      else:
         ##print "some non-hit gems"
         for gem in untouched_gems:
            self.beatmatchdisplay.gem_pass(gem)

   def draw_gems(self):
      #print "in draw_gems"
      current_tick = self.audio_ctrl.song.cond.get_tick()
      top_of_screen = (current_tick)/4 - 600
      bottom_of_screen = (current_tick)/4 + 50

      ##print "top_of_screen: " + str(top_of_screen)
      ##print "bottom_of_screen: " + str(bottom_of_screen)

      drawable_gems = self.gemdata.get_gems_in_range(top_of_screen, bottom_of_screen)
      #print "drawable_gems is: " + str(drawable_gems)

      self.beatmatchdisplay.draw_gems(drawable_gems)   

      
run(MainWidget)
