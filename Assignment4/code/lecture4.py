#lecture4.py

import sys
sys.path.append('./common')
from core import *
from audio import *
from synth import *
from clock_lec import *
from modifier import *

from kivy.uix.label import Label


# Let's use fluid synth to play notes
kKeys = '1234567890'
kPitches = (36,60,62,64,65,67,69,71,72,74,76)


# this demonstrates the fluidsynth synthesizer.
class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      print 'reverb params', self.synth.get_reverb_params()
      self.synth.set_reverb_params(.5, 0, .5, .9)
      print 'reverb params', self.synth.get_reverb_params()
      self.synth.set_reverb_on(True)

      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)


      modifiers = (('a', "program", range(128), lambda x: self.synth.program_change(0, x)),
                   ('s', "vibrato", range(128), lambda x: self.synth.cc(0, 1, x)),
                   ('d', "volume",  range(128), lambda x: self.synth.cc(0, 7, x)),
                   ('f', "sustain", range(128), lambda x: self.synth.cc(0, 64, x)),
                   ('g', "reverb",  range(128), lambda x: self.synth.cc(0, 91, x)),
                   ('z', "bend",  np.linspace(-8192, 8191, 128), lambda x: self.synth.pitch_bend(0, int(x))))

      self.mods = [Modifier(*m) for m in modifiers]

   def on_key_down(self, keycode, modifiers):
      for m in self.mods:
         m.on_key_down(keycode[1])

      if keycode[1] in kKeys:
         pitch = kPitches[ kKeys.index(keycode[1]) ]
         self.synth.noteon(0, pitch, 100)

   def on_key_up(self, keycode):
      for m in self.mods:
         m.on_key_up(keycode[1])

      if keycode[1] in kKeys:
         pitch = kPitches[ kKeys.index(keycode[1]) ]
         self.synth.noteoff(0, pitch)

   def on_update(self) :
      self.label.text = ''
      for m in self.mods:
         m.on_update()
         self.label.text += m.get_txt() + '\n'


# Now, let's test the Clock and Conductor classes
class MainWidget2(BaseWidget) :
   def __init__(self):
      super(MainWidget2, self).__init__()

      self.audio = Audio()
      self.synth = Synth('../FluidR3_GM.sf2')
      self.audio.add_generator(self.synth)

      # create a clock and conductor
      self.clock = Clock()
      self.cond = Conductor(self.clock, 120)

      # and text to display our status      
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'c':
         self.clock.toggle()

   def on_update(self) :
      self.label.text = self.cond.now_str()



# Now, let's test the scheduler class
class MainWidget3(BaseWidget) :
   def __init__(self):
      super(MainWidget3, self).__init__()

      # create a clock and conductor
      self.clock = Clock()
      self.cond = Conductor(self.clock, 120)

      # create a new scheduler
      self.sched = Scheduler(self.cond)

      # and text to display our status      
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      # add another text to display results of scheduling:
      self.label2 = Label(text = "text\n", pos=(350, 400), text_size=(150,200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label2)

   def on_key_down(self, keycode, modifiers):
      if keycode[1] == 'a':
         print 'post'
         now = self.cond.get_tick()
         later = now + (2 * kTicksPerQuarter)
         self.sched.post_at_tick(later, self.hit_me, 'hello')

      if keycode[1] == 'c':
         self.clock.toggle()

   def hit_me(self, tick, msg):
      self.label2.text += "%s (at %d)\n" % (msg, tick)

   def on_update(self) :
      # scheduler gets poked every frame
      self.sched.on_update()
      self.label.text = self.cond.now_str()


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
         self.clock.toggle()

      if keycode[1] == 'm':
         self.metro.start()

      if keycode[1] == 'up':
         self.cond.bpm += 10

      if keycode[1] == 'down':
         self.cond.bpm -= 10

   def on_update(self) :
      # scheduler gets poked every frame
      self.sched.on_update()
      self.label.text = self.cond.now_str()


# pass in which MainWidget to run as a command-line arg
run(eval('MainWidget' + sys.argv[1]))

