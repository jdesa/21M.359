#####################################################################
#
# tracks.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from clock_lec import kTicksPerQuarter
from song_lec import *
from wavegen import *


# A class that tick on every beat.
class Metronome(Track):
   def __init__(self, synth):
      super(Metronome, self).__init__()
      self.synth = synth

      self.beat_len = kTicksPerQuarter
      self.pitch = 60
      self.channel = 0

      # run-time variables
      self.on_cmd = None
      self.off_cmd = None

   def start(self):
      print 'metro start'
      self.synth.program(self.channel, 128, 0)

      now = self.song.cond.get_tick()
      next_beat = now - (now % self.beat_len) + self.beat_len
      self._post_at(next_beat)

   def stop(self):
      print 'metro stop'

      self.song.sched.remove(self.on_cmd)
      self.song.sched.remove(self.off_cmd)

      if self.off_cmd:
         self.off_cmd.execute()

      self.on_cmd = None
      self.off_cmd = None

   def _post_at(self, tick):
      self.on_cmd = self.song.sched.post_at_tick(tick, self._noteon)

   def _noteon(self, tick, ignore):
      # play the note right now:
      self.synth.noteon(self.channel, self.pitch, 100)
      
      # post the note off for later:
      self.off_cmd = self.song.sched.post_at_tick(tick + self.beat_len/2, self._noteoff, self.pitch)

      # schedule the next note on one beat later
      next_beat = tick + self.beat_len
      self._post_at(next_beat)

   def _noteoff(self, tick, pitch):
      self.synth.noteoff(self.channel, pitch)



# Appegiator Track. Will arppegiate a set of notes to a specific rhythm and note direction
# set_notes, set_rhythm, set_direction can all be called at any point in time.
class Arpeggiator(Track):
   def __init__(self, synth, channel, bank, preset, callback = None):
      super(Arpeggiator, self).__init__()
      # output parameters
      self.synth = synth
      self.channel = channel
      self.cbp = (channel, bank, preset)
      self.callback = callback

      # arpeggio parameters:
      self.note_grid = kTicksPerQuarter / 4
      self.note_len_ratio = 0.75
      self.notes = [60, 64, 67, 72]
      self.direction = 'up'

      # run-time variables
      self.cur_idx = 0
      self.idx_inc = 1
      self.on_cmd = None
      self.off_cmd = None

   def start(self):
      self.synth.program(*self.cbp)
      now = self.song.cond.get_tick()
      next_tick = now - (now % self.note_grid) + self.note_grid
      self._post_at(next_tick)

   def stop(self):
      self.song.sched.remove(self.on_cmd)
      self.song.sched.remove(self.off_cmd)
      if self.off_cmd:
         self.off_cmd.execute()
   
   # notes is a list of MIDI pitch values. For example [60 64 67 72]
   def set_notes(self, notes):
      self.notes = notes
      if self.cur_idx >= len(notes):
         self.cur_idx = len(notes) - 1

   def set_rhythm(self, note_grid, note_len_ratio):
      self.note_grid = note_grid
      self.note_len_ratio = note_len_ratio

   # dir is either 'up', 'down', or 'updown'
   def set_direction(self, direction):
      assert (direction == 'up' or direction == 'down' or direction == 'updown')
      self.direction = direction
      if direction == 'up':
         self.idx_inc = 1
      elif direction == 'down':
         self.idx_inc = -1

   def _get_next_pitch(self):
      pitch = self.notes[self.cur_idx]

      notes_len = len(self.notes)

      # flip detection if 'updown' and at endpoint
      if self.direction == 'updown':
         if self.cur_idx == 0:
            self.idx_inc = 1
         elif self.cur_idx == notes_len-1:
            self.idx_inc = -1

      # advance index
      self.cur_idx += self.idx_inc

      # keep in bounds:
      self.cur_idx = self.cur_idx % notes_len

      return pitch

   def _post_at(self, tick):
      self.on_cmd  = self.song.sched.post_at_tick(tick, self._noteon, None)

   def _noteon(self, tick, ignore):
      pitch = self._get_next_pitch()

      # play note on:
      velocity = 60
      self.synth.noteon(self.channel, pitch, velocity)

      # post note-off:
      duration = self.note_len_ratio * self.note_grid
      off_tick = tick + duration
      self.off_cmd = self.song.sched.post_at_tick(off_tick, self._noteoff, pitch)

      # callback:
      if self.callback:
         self.callback(tick, pitch, velocity, duration)

      # post next note. quantize tick to line up with grid of current note length
      tick -= tick % self.note_grid
      next_beat = tick + self.note_grid
      self._post_at(next_beat)

   def _noteoff(self, tick, pitch):
      self.synth.noteoff(self.channel, pitch)



# audio track - very simple wrapper around wavegen
class AudioTrack(Track):
   def __init__(self, audio, filepath):
      super(AudioTrack, self).__init__()
      self.wavegen = WaveFileGenerator(filepath)
      self.wavegen.stop()
      audio.add_generator(self.wavegen)

   def start(self):
      print 'audio start'
      self.wavegen.start()

   def stop(self):
      print 'audio stop'
      self.wavegen.stop()

