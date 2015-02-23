# pset2.py

import sys
sys.path.append('./common')
from core import *
from audio import *
from note import *
from wavegen import *


class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      self.wave = WaveFileGenerator("HideAndSeek16.wav")
      self.songregions = SongRegions("hideandseek16_regions.txt", "HideAndSeek16.wav")
      self.wavesnippets = self.songregions.make_snippits()
      self.snippets = {}
      self.snippet_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
      self.new_region_start = 0.0
      self.new_region_end = 0.0

   def on_key_down(self, keycode, modifiers):
      print keycode[1]

      if keycode[1] in self.snippet_list:
         if keycode[1] in self.wavesnippets.keys():
            newgen = self.wavesnippets[keycode[1]].make_generator(True, 1.0)
            self.snippets[keycode[1]] = newgen
            self.audio.add_generator(newgen)

      if keycode[1] == "up":
         new_gain = self.audio.get_gain() * 1.1
         self.audio.set_gain(new_gain)
         print self.audio.get_gain()

      elif keycode[1] == "down":
         new_gain = self.audio.get_gain() / 1.1
         self.audio.set_gain( new_gain )
         print self.audio.get_gain()

      elif keycode[1] == "spacebar":
         self.wave.play_toggle()

      elif keycode[1] == "enter":
         self.audio.add_generator(self.wave)

      elif keycode[1] == "shift":
         self.wave.reset()

      elif keycode[1] == "[":
         for generator in self.snippets.keys():
            generator.dec_speed()

      elif keycode[1] == "]":
         for generator in self.snippets.keys():
            generator.inc_speed()

      elif keycode[1] == "'":
         print "here! keydown"
         self.new_region_start = self.wave.frames
         print "new_region_start: " + str(self.new_region_start)

   def on_key_up(self, keycode):
      if keycode[1] in self.wavesnippets.keys():
         self.snippets.pop(keycode[1], None)
         self.wavesnippets[keycode[1]].generator.stop_generator()

      if keycode[1] == "'":
         print "here! keyup"
         self.new_region_end = self.wave.frames
         print "new region end " + str(self.new_region_end)
         for number in [item for item in self.snippet_list if item not in self.wavesnippets.keys()]:
               print number
               self.wavesnippets[number] = WaveSnippet(self.wave.reader, self.new_region_start, self.new_region_end)
               break
         

run(MainWidget)
