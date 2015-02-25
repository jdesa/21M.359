# pset2.py

import sys
sys.path.append('./common')
from core import *
from audio import *
from note import *
from wavegen import *


# I collaborated with Nick Benson in class and with CK Ong, Kevin King, and Polly Li on general concepts and debugging help outside of class.
# Credit to Kevin King for the idea of speeding up and slowing down the entirety of self.data instead of in buffered chunks (which is more complicated)
# Youtube Link: 

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
            self.snippets[generator].dec_speed()

      elif keycode[1] == "]":
         for generator in self.snippets.keys():
            self.snippets[generator].inc_speed()

      elif keycode[1] == "'":
         self.new_region_start = self.wave.frames
         print "started new region " + str(self.new_region_start)

      elif keycode[1] == "backspace":
          for generator in self.snippets.keys():
            self.snippets[generator].stop_generator()

   def on_key_up(self, keycode):
      if keycode[1] in self.wavesnippets.keys():
            self.snippets.pop(keycode[1], None)
            self.wavesnippets[keycode[1]].generator.stop_generator()

      if keycode[1] == "'":
         self.new_region_end = self.wave.frames
         print 'new_region_end' + str(self.wave.frames)
         for number in [snippet_name for snippet_name in self.snippet_list if snippet_name not in self.wavesnippets.keys()]:
               self.wavesnippets[number] = WaveSnippet(WaveReader("HideAndSeek16.wav"), self.new_region_start, self.new_region_end - self.new_region_start)
               break

run(MainWidget)
