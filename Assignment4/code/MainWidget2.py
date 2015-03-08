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
         print "c"
         self.clock.toggle()

      if keycode[1] == 'm':
         self.metro.start()

      if keycode[1] == 'up':
         print "up"
         self.cond.bpm += 10

      if keycode[1] == 'down':
         print "down"
         self.cond.bpm -= 10

   def on_update(self) :
      # scheduler gets poked every frame
      self.sched.on_update()
      self.label.text = self.cond.now_str()

