# arpeg.py

# Create an arpeggiator class.

class Arpeggiator(object):
   def __init__(self, synth, sched, channel, bank, preset):
      super(Arpeggiator, self).__init__()
      pass
 
   def start(self):
      pass
 
   def stop(self):
      pass
   
   # notes is a list of MIDI pitch values. For example [60 64 67 72]
   def set_notes(self, notes):
      pass
 
   # note_grid is a value in ticks that defines the rhythmic pulse of the
   # arpeggiator. For example, kTicksPerQuarter means quarter-note rhythm
   # kTicksPerQuarter/3 means triplets.
   #
   # note_len_ratio is how short or long the note length should be.
   # a value of 1 means play full value. .5 means the note should turn off
   # at 50% of the rhymic pulse.
   def set_rhythm(self, note_grid, note_len_ratio):
      pass
 
   # direction is either 'up', 'down', or 'updown'
   def set_direction(self, direction):
      pass
