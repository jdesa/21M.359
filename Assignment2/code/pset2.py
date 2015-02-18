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

   def on_key_down(self, keycode, modifiers):

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
         print "Wave"

   def on_key_up(self, keycode):
      pass

run(MainWidget)
