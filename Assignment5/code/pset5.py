#pset5 template

import sys
sys.path.append('./common')
from core import *
from audio import *
from synth import *

from song_lec import *
from tracks_lec import *

from chord import *

from kivy.uix.label import Label
from kivy.core.window import Window
from random import random

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock


# A class that monitors the current tick, Chordmap, and mouse-position.
# From that, it modifies attributes of Arpeggiator (notes, rhythms)
class Adaptor(object):
   def __init__(self, arg1, arg2):   # args TBD 
      super(Adaptor, self).__init__()
      
   def on_update(self):
      # most of the work happens here
      pass      

   def get_info(self):
      # return useful info/debugging text you want to see on every update.
      return ''


class Graphics(InstructionGroup):
   def __init__(self):
      super(Graphics, self).__init__()

   def on_update(self, dt):
      pass


class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()

      # text to display our status
      self.label = Label(text = "text", pos=(100, 500), text_size=(150,100), valign='top')
      self.add_widget(self.label)

      self.audio = Audio()
      self.synth = Synth('FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      self.song = Song()

      # add AudioTrack, Arpeggiator, Metronome (if you wish)
      # set up Tempo Track correctly.

      # create chordmap for the song

      self.adaptor = Adaptor('foo', 'bar')

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'p':
         self.song.toggle()

      # Add whatever else you might need


   def on_update(self) :
      self.adaptor.on_update()
      self.song.on_update()

      # TODO - update graphics system...

      self.label.text = self.song.cond.now_str() + self.adaptor.get_info()


run(MainWidget)
