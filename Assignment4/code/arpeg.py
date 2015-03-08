# arpeg.py

# Create an arpeggiator class.
kTicksPerQuarter = 480

class Arpeggiator(object):
   def __init__(self, sched, synth, pulse, notes):
      self.sched = sched
      self.synth = synth
      self.beat_len = kTicksPerQuarter
      self.channel = 0
      self.started = False
      #list of pitch values of notes
      self.notes = notes
      self.pulse = pulse
      self.note_len_ratio = 1
      self.pitch = self.notes[0]
      self.going_up = True
      self.updown = False
 
   def start(self):
      if self.started == False:
         self.started = True

         print 'Metronome start'
         #self.synth.program(self.channel, 128, 0)
         self.synth.program(self.channel, 0, 19)

         now = self.sched.cond.get_tick()
         next_beat = now - (now % self.beat_len) + self.beat_len
         self._post_at(next_beat)
 
   def stop(self):
      self.started = False
      self.synth.noteoff(self.channel, self.pitch)    
   
   # notes is a list of MIDI pitch values. For example [60 64 67 72]
   def set_notes(self, notes):
      self.notes = notes
 
   # note_grid is a value in ticks that defines the rhythmic pulse of the
   # arpeggiator. For example, kTicksPerQuarter means quarter-note rhythm
   # kTicksPerQuarter/3 means triplets.
   #
   # note_len_ratio is how short or long the note length should be.
   # a value of 1 means play full value. .5 means the note should turn off
   # at 50% of the rhymic pulse.
   def set_rhythm(self, note_grid, note_len_ratio):
      self.pulse = note_grid
      self.note_len_ratio = note_len_ratio
 
   # direction is either 'up', 'down', or 'updown'
   def set_direction(self, direction):
      if direction == "updown":
         self.updown = not self.updown
      else:
         if direction == 'up':
            self.going_up = True
         elif direction == "down":
            self.going_up = False
   
   def _post_at(self, tick):
      print "post at"
      if self.started == True:
         self.sched.post_at_tick(tick, self._noteon)

   def get_next_pitch(self):
      for i in range(len(self.notes)):
         if self.notes[i] == self.pitch:
            
            if self.updown == True:
               if i == len(self.notes) - 1 or i == 0:
                  self.going_up = not self.going_up
                  print "i is: " + str(i)
                  print "are we going up?: " + str(self.going_up)
                  #reverse direction
            
            if self.going_up:
               self.pitch = self.notes[(i + 1) % len(self.notes)]
               print "going up pitch: " + str(self.pitch)
               break
            else:
               self.pitch = self.notes[(i - 1)]
               print "going down pitch: " + str(self.pitch)
               break

            break

   def _noteon(self, tick, ignore):
      if self.started == True:
         # play the note right now:
            print "in note on"
            print "_noteon self.pitch is: " + str(self.pitch)
            self.get_next_pitch()
            self.synth.noteon(self.channel, self.pitch, 100)
            
            # post the note off for later:
            self.sched.post_at_tick(tick + self.beat_len/2, self._noteoff, self.pitch)

            # schedule the next note on one beat later
            next_beat = tick + self.beat_len
            self._post_at(next_beat)

   def _noteoff(self, tick, pitch):
      self.synth.noteoff(self.channel, pitch)    

   def stop(self):
      self.sched.stop()
      self.started = False  