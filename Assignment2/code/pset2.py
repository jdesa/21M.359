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
      self.snippet_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

   def on_key_down(self, keycode, modifiers):

      print keycode[1] 

      if keycode[1] in self.snippet_list:
         print "in snippet_list"
         print self.wavesnippets.keys()
         if keycode[1] in self.wavesnippets.keys():
            print "in wavesnippet keys"
            self.audio.add_generator(self.wavesnippets[keycode[1]].make_generator())
            print self.audio.generators

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


   def on_key_up(self, keycode):
      if keycode[1] in self.snippet_list:
         if keycode[1] in self.wavesnippets.keys():
            self.wavesnippets[keycode[1]].generator.stop_generator()

run(MainWidget)
