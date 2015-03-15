#lecture5.py

import sys
sys.path.append('../common')
from core import *
from audio import *
from synth import *

from clock_lec import *
from song_lec import *
from tracks_lec import *


from kivy.uix.label import Label

kDirections = { '1':'up', '2':'down', '3':'updown' }

# 1. Create a song class that encapsulates elements we have
# worked on so far: clock, sched, cond.
class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()

      # text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      self.song = Song()
      self.song.add_track( Metronome( self.synth ) )
      self.arp = Arpeggiator(self.synth, 1, 0, 40)
      self.song.add_track( self.arp )
      self.arp.set_notes([60, 64, 67, 70, 72])
      
   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'p':
         self.song.toggle()

      if keycode[1] in kDirections:
         self.arp.set_direction( kDirections[ keycode[1] ])
      
      if keycode[1] == 'up':
         bpm = self.song.cond.get_bpm()
         bpm = np.clip(bpm * 1.03, 20, 300)
         self.song.cond.set_bpm( bpm )

      if keycode[1] == 'down':
         bpm = self.song.cond.get_bpm()
         bpm = np.clip(bpm / 1.03, 20, 300)
         self.song.cond.set_bpm( bpm )

   def on_update(self) :
      self.song.on_update()
      self.label.text = self.song.cond.now_str() + '\n'
      self.label.text += 'bpm:%.1f\n' % self.song.cond.get_bpm()



# Creating a tempo track and test it out
class MainWidget2(BaseWidget) :
   def __init__(self):
      super(MainWidget2, self).__init__()

      # text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      self.song = Song()
      self.song.add_track( Metronome( self.synth ) )
      self.arp = Arpeggiator(self.synth, 1, 0, 40)
      self.song.add_track( self.arp )

      # test out a tempo map:
      data = [(0,0), (4.0, kTicksPerQuarter*4), (8.0, kTicksPerQuarter*12), 
               (12.0, kTicksPerQuarter*14)]
      tempo_map = TempoMap1(data)
      self.song.cond.set_tempo_map(tempo_map)

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'p':
         self.song.toggle()

      if keycode[1] in kDirections:
         self.arp.set_direction( kDirections[ keycode[1] ])

   def on_update(self) :
      self.song.on_update()
      self.label.text = self.song.cond.now_str() + '\n'
      self.label.text += 'bpm:%.1f\n' % self.song.cond.get_bpm()


# Add an audio track
class MainWidget3(BaseWidget) :
   def __init__(self):
      super(MainWidget3, self).__init__()

      # text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      self.song = Song()
      self.song.add_track( Metronome( self.synth ) )
      self.song.add_track( AudioTrack( self.audio, 'Chameleon.wav'))

      tempo_map = TempoMap(filepath = 'Chameleon_tempo.txt')
      self.song.cond.set_tempo_map(tempo_map)

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'p':
         self.song.toggle()
         
   def on_update(self) :
      self.song.on_update()
      self.label.text = self.song.cond.now_str() + '\n'
      self.label.text += 'bpm:%.1f\n' % self.song.cond.get_bpm()



# Add a real TempoMap to the song
class MainWidget4(BaseWidget) :
   def __init__(self):
      super(MainWidget4, self).__init__()

      # text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      self.song = Song()
      self.song.add_track( Metronome( self.synth ) )
      self.song.add_track( AudioTrack( self.audio, 'Chameleon.wav'))
      self.arp = Arpeggiator(self.synth, 1, 0, 84)
      self.song.add_track( self.arp )

      tempo_map = TempoMap(filepath = 'Chameleon_tempo.txt')
      self.song.cond.set_tempo_map(tempo_map)

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'p':
         self.song.toggle()

      if keycode[1] in kDirections:
         self.arp.set_direction( kDirections[ keycode[1] ])
         
      if keycode[1] == 'a':
         self.arp.set_notes([58, 61, 65, 68]) # Bbm7

      if keycode[1] == 's':
         self.arp.set_notes([63, 67, 70, 73]) # Eb7

   def on_update(self) :
      self.song.on_update()
      self.label.text = self.song.cond.now_str() + '\n'
      self.label.text += 'bpm:%.1f\n' % self.song.cond.get_bpm()

   def on_note_cb(self, tick, pitch, velocity, duration) :
      print 'note:', tick, pitch, velocity, duration


# pass in which MainWidget to run as a command-line arg
run(eval('MainWidget' + sys.argv[1]))

