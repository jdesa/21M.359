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
      self.songregions = SongRegions("hideandseek16_regions.txt")
      self.wavesnippets = self.songregions.make_snippets()

   def on_key_down(self, keycode, modifiers):
      snippet_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

      if keycode[1] in snippet_list:
         if keycode[1] in self.wavesnippets.keys:
            self.audio.add_generator(WaveFileGenerator("HideAndSeek16.wav").make_generator()))

      if keycode[1] == "up":
         new_gain = self.audio.get_gain() * 1.1
         self.audio.set_gain( new_gain )
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
         print "Halp"
         self.wave.reset()


   def on_key_up(self, keycode):
      pass

run(MainWidget)
