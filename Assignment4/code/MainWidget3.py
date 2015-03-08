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
      p
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