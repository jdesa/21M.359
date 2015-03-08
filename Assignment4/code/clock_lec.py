# lecture 4 audio:

import time


# Simple time keeper object. It starts at 0 and knows how to pause
class Clock(object):
   def __init__(self):
      super(Clock, self).__init__()
      self.paused = True
      self.offset = 0

   def get_time(self):
      if self.paused:
         return self.offset
      else:
         return self.offset + time.time()

   def start(self):
      if self.paused:
         self.paused = False
         self.offset -= time.time()

   def stop(self):
      if not self.paused:
         self.paused = True
         self.offset += time.time()

   def toggle(self):
      if self.paused:
         self.start()
      else:
         self.stop()


# The conductor object - converts from time to ticks based on tempo
kTicksPerQuarter = 480

class Conductor(object):
   def __init__(self, clock, bpm = 120) :
      super(Conductor, self).__init__()
      self.bpm = bpm
      self.clock = clock
      self.tick_offset = 0

   def get_time(self) :
      return self.clock.get_time()

   def get_tick(self) :
      sec = self.get_time()
      tick = sec * (self.bpm / 60.) * kTicksPerQuarter - self.tick_offset
      return int(tick)

   def now_str(self):
      time = self.get_time()
      tick = self.get_tick()
      beat = float(tick) / kTicksPerQuarter
      txt = "time:%.2f\ntick:%d\nbeat:%.2f" % (time, tick, beat)
      return txt

   def set_bpm(self, bpm):
      print "prev tick: " + str(self.get_tick())
      self.tick_offset = self.get_time()* (bpm / 60.) * kTicksPerQuarter - self.get_tick()
      print "tick offset: " + str(self.tick_offset)
      self.bpm = bpm
      print "new tick: " + str(self.get_tick())


   def get_bpm(self):
      return self.bpm

# next, we build a scheduler that knows how to execute code 
# at a future time - or more importantly, at a future tick.
class Scheduler(object):
   def __init__(self, cond) :
      super(Scheduler, self).__init__()
      self.cond = cond
      self.commands = []

   # add a record for the function to call at the particular tick
   # keep the list of commands sorted from lowest to hightest tick
   # make sure tick is the first argument so sorting will work out
   # properly
   def post_at_tick(self, tick, func, arg = None) :
      now = self.cond.get_tick()

      if tick <= now:
         func(tick, arg)
      else:
         self.commands.append(Command(tick, func, arg))
         self.commands.sort(key = lambda x: x.tick)

   # on_update should be called as often as possible.
   # the only trick here is to make sure we remove the command BEFORE
   # calling the command's function.
   def on_update(self):
      now = self.cond.get_tick()
      while self.commands:
         if self.commands[0].should_exec(now):
            command = self.commands.pop(0)
            command.execute()
         else:
            break

 
class Command(object):
   def __init__(self, tick, func, arg):
      super(Command, self).__init__()
      self.tick = tick
      self.func = func
      self.arg = arg
      
   def should_exec(self, tick) :
      return self.tick <= tick

   def execute(self):
      self.func( self.tick, self.arg )

   def __repr__(self):
      return 'cmd:%d' % self.tick


# finally, let's exercise these object by building a simple metronome
class Metronome(object):
   def __init__(self, sched, synth):
      super(Metronome, self).__init__()
      self.sched = sched
      self.synth = synth

      self.beat_len = kTicksPerQuarter
      self.pitch = 60
      self.channel = 0

   def start(self):
      print 'Metronome start'
      self.synth.program(self.channel, 128, 0)
      #self.synth.program(self.channel, 0, 19)

      now = self.sched.cond.get_tick()
      next_beat = now - (now % self.beat_len) + self.beat_len
      self._post_at(next_beat)

   def _post_at(self, tick):
      self.sched.post_at_tick(tick, self._noteon)

   def _noteon(self, tick, ignore):
      # play the note right now:
      self.synth.noteon(self.channel, self.pitch, 100)
      
      # post the note off for later:
      self.sched.post_at_tick(tick + self.beat_len/2, self._noteoff, self.pitch)

      # schedule the next note on one beat later
      next_beat = tick + self.beat_len
      self._post_at(next_beat)

   def _noteoff(self, tick, pitch):
      self.synth.noteoff(self.channel, pitch)      

