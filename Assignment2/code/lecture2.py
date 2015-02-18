# lecture2.py
#
# today, we will read note data. As a review of last week's assignments, I
# have a dumb down version. Hopefully you all have created more interesting
# versions.


import sys
sys.path.append('./common')
from core import *
from audio import *
from note import *
from wavegen import *


kPitches1 = (60,62,64,65,67,69,71,72,74)

# basic audio - plays notes. gain +/-
class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()

      self.audio = Audio()

   def on_key_down(self, keycode, modifiers):
      if keycode[0] >= ord('1') and keycode[0] <= ord('9'):
         pitch = kPitches1[ keycode[0] - ord('1') ]
         print 'pitch = ', pitch
         note = NoteGenerator(pitch, 0.2, 2)
         self.audio.add_generator(note)
      
      elif keycode[1] == "up":
         new_gain = self.audio.get_gain() * 1.1
         self.audio.set_gain( new_gain )
         print self.audio.get_gain()

      elif keycode[1] == "down":
         new_gain = self.audio.get_gain() / 1.1
         self.audio.set_gain( new_gain )
         print self.audio.get_gain()



# add wave file playback
# make new pitch set
# reduce note duration to 1.
kPitches2 = (61,63,65,66,68,70,73,75,78)

class MainWidget2(BaseWidget) :
   def __init__(self):
      super(MainWidget2, self).__init__()

      self.audio = Audio()
      self.wave = WaveFileGenerator("superstition.wav")

   def on_key_down(self, keycode, modifiers):
      if keycode[0] >= ord('1') and keycode[0] <= ord('9'):
         pitch = kPitches2[ keycode[0] - ord('1') ]
         print 'pitch = ', pitch
         note = NoteGenerator(pitch, 0.2, .4)
         self.audio.add_generator(note)
      
      elif keycode[1] == 'w':
         print 'Wave'
         self.audio.add_generator(self.wave)

      elif keycode[1] == "up":
         self.audio.set_gain( self.audio.get_gain() * 1.1 )

      elif keycode[1] == "down":
         self.audio.set_gain( self.audio.get_gain() / 1.1 )


## add snippet playback
class MainWidget3(BaseWidget) :
   def __init__(self):
      super(MainWidget3, self).__init__()

      self.audio = Audio()
      self.wave = WaveFileGenerator("superstition.wav")

      # create a WaveReader - knows how to get data from a wave file:
      reader = WaveReader("superstition.wav")
      self.snip1 = WaveSnippet(reader, kSamplingRate * 2, kSamplingRate * 2)
      self.snip2 = WaveSnippet(reader, kSamplingRate * 22, kSamplingRate * 1)

   def on_key_down(self, keycode, modifiers):
      #print 'key-down', keycode, modifiers
      if keycode[0] >= ord('1') and keycode[0] <= ord('9'):
         pitch = kPitches2[ keycode[0] - ord('1') ]
         print 'pitch = ', pitch
         note = NoteGenerator(pitch, 0.5, 1)
         self.audio.add_generator(note)
      
      elif keycode[1] == 'w':
         print 'Wave'
         self.audio.add_generator(self.wave)

      elif keycode[1] == 'a':
         print 'a'
         gen = self.snip1.make_generator()
         self.audio.add_generator(gen)

      elif keycode[1] == 's':
         print 's'
         gen = self.snip2.make_generator()
         self.audio.add_generator(gen)

      elif keycode[1] == "up":
         self.audio.set_gain( self.audio.get_gain() * 1.1 )

      elif keycode[1] == "down":
         self.audio.set_gain( self.audio.get_gain() / 1.1 )

run(MainWidget3)
