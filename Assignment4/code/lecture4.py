#lecture4.py
import sys
sys.path.append('./common')
from core import *
from audio import *
from synth import *
from clock_lec import *
from modifier import *
from arpeg import *
from kivy.uix.label import Label


# Let's use fluid synth to play notes
kKeys = '1234567890'
kPitches = (36,60,62,64,65,67,69,71,72,74,76)

# Finally, let's test the Metronome class
class MainWidget4(BaseWidget) :
   def __init__(self):
      super(MainWidget4, self).__init__()

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      # create clock, conductor, scheduler
      self.clock = Clock()
      self.cond = Conductor(self.clock, 120)
      self.sched = Scheduler(self.cond)

      # create the metronome:
      self.metro = Metronome(self.sched, self.synth)
      self.metro_on = False

      self.arpeg = Arpeggiator(self.sched, self.synth, 1, [60, 64, 67, 72, 76])

      # and text to display our status      
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

   def on_key_down(self, keycode, modifiers):
      if keycode[0] >= ord('1') and keycode[0] <= ord('9'):
         pitch = kPitches[ keycode[0] - ord('1') ]
         print pitch
         self.synth.noteon(0, pitch, 100)

      if keycode[1] == 'c':
         print "c"
         self.clock.toggle()

      if keycode[1] == 'm':
         if self.metro_on == False:
            self.metro.start()
            self.metro_on = True
         else:
            print "in stop"
            self.metro.stop()
            self.metro_on = False

      if keycode[1] == 'up':
         print "up"
         self.cond.set_bpm(self.cond.bpm+1)
         print self.cond.bpm

      if keycode[1] == 'down':
         print "down"
         self.cond.set_bpm(self.cond.bpm-1)

      if keycode[1] == 'left':
         self.cond.change_tempo_marking(-1)

      if keycode[1] == 'right':
         self.cond.change_tempo_marking(1)

      if keycode[1] == 'a':
         self.arpeg.start()

   def on_update(self) :
      # scheduler gets poked every frame
      self.sched.on_update()
      self.label.text = self.cond.now_str()


# pass in which MainWidget to run as a command-line arg
run(eval('MainWidget4'))

