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
      self.synth_metro = Synth('../FluidR3_GM.sf2')
      self.synth_arpeg = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth_metro)
      self.audio.add_generator(self.synth_arpeg)

      # create clock, conductor, scheduler
      self.clock = Clock()
      self.cond = Conductor(self.clock, 120)
      self.sched = Scheduler(self.cond)

      # create the metronome:
      self.metro = Metronome(self.sched, self.synth_metro)
      self.metro_on = False

      self.arpeg = Arpeggiator(self.sched, self.synth_arpeg, 4.0, [60, 64, 67, 72, 76]) 
      self.arpeg_on = False
      self.arpeg_select = False
      #self.arpeg2 = Arpeggiator(self.sched, self.synth_arpeg, 4.0, [60-12, 64-12, 67-12, 72-12, 76-12])

      self.record_arpeg_on = False
      self.recorded_arpeg_notes = []

      self.set_arpeg_pulse = False
      self.arpeg_pulse = ''
      self.valid_pulses = ['1', '2', '3', '4', '8', '16']


      # and text to display our status      
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)


   def on_key_down(self, keycode, modifiers):
      if keycode[0] >= ord('1') and keycode[0] <= ord('9'):
         pitch = kPitches[ keycode[0] - ord('1') ]
         if self.record_arpeg_on:
            self.recorded_arpeg_notes.append(pitch)
         elif self.set_arpeg_pulse:
            self.arpeg_pulse += keycode[1]
            print self.arpeg_pulse
         else:
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
         if self.arpeg_on == False:
            self.arpeg.start()
            #elf.arpeg2.start()
            self.arpeg_on = True
         else:
            print "in stop"
            self.arpeg.stop()
            #self.arpeg2.stop()
            self.arpeg_on = False
      
      if keycode[1] == '[':
         self.arpeg.set_direction('down')
      elif keycode[1] == ']':
         self.arpeg.set_direction('up')
      elif keycode[1] == '\\':
         self.arpeg.set_direction('updown') 
      elif keycode[1] == "enter":
         self.record_arpeg_on = True
      elif keycode[1] == "shift":
         print "in shift!"
         self.set_arpeg_pulse = True
      
      elif keycode[1] == ",":
         self.arpeg.set_rhythm(self.arpeg.pulse, 1.5)
      elif keycode[1] == ".":
         self.arpeg.set_rhythm(self.arpeg.pulse, .5)
      elif keycode[1] == '/':
         self.arpeg.set_rhythm(self.arpeg.pulse, 1.0)



   def on_key_up(self, keycode):
      if keycode[1] == "enter" and len(self.recorded_arpeg_notes) > 1:
         self.record_arpeg_on = False
         self.arpeg.set_notes(self.recorded_arpeg_notes)
         print "recorded arpeg: " + str(self.recorded_arpeg_notes)
         self.recorded_arpeg_notes = []

      if keycode[1] == "shift":
         self.set_arpeg_pulse = False
         print "arpeg pulse is: " + str(self.arpeg_pulse)
         if self.arpeg_pulse in self.valid_pulses:
            self.arpeg.set_rhythm(int(self.arpeg_pulse), self.arpeg.note_len_ratio)
         self.arpeg_pulse = ''

   def on_update(self) :
      # scheduler gets poked every frame
      self.sched.on_update()
      self.label.text = self.cond.now_str()


# pass in which MainWidget to run as a command-line arg
run(eval('MainWidget4'))

