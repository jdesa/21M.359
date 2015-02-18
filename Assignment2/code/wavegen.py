# wavegen - Lecture file

import numpy as np
import wave
from audio import kSamplingRate


# now, lets make a class that can hold samples in memory so that it
# can access them quickly and repeatedly. But, first, we just typed a bunch of code
# to read wave data and convert to mono-float. Let's abstract that and reuse it:
class WaveReader(object):
   def __init__(self, filepath) :
      super(WaveReader, self).__init__()

      self.wave = wave.open(filepath)
      self.channels, self.sampwidth, self.sr, self.end, \
         comptype, compname = self.wave.getparams()
      
      # for now, we will only accept stereo, 16 bit files      
      assert(self.channels == 2)
      assert(self.sampwidth == 2)
      assert(self.sr == 44100)

   # read an arbitrary chunk of an arbitrary length
   def read(self, num_frames) :
      # get the raw data from wave file as a byte string.
      # will return num_frames, or less if too close to end of file
      raw_bytes = self.wave.readframes(num_frames)

      frames_read = len(raw_bytes) / (self.sampwidth * self.channels)

      # convert to numpy array, where the dtype is int16 or int8
      samples = np.fromstring(raw_bytes, dtype = np.int16)

      # convert from integer type to floating point, and scale to [-1, 1]
      samples = samples.astype(np.float32)
      samples *= (1 / 32768.0)

      return samples

   # but allow us to change the "play head" in the wave file
   def set_pos(self, frame) :
      self.wave.setpos(frame)



# now the wave file generator is much smaller. Most of the code is just dealing
# with the end condition
class WaveFileGenerator(object):
   def __init__(self, filepath) :
      super(WaveFileGenerator, self).__init__()
      self.playing = True
      self.reader = WaveReader(filepath)

   def generate(self, num_frames) :
      if self.playing:
         output = self.reader.read(num_frames)
      else:
         output = np.zeros(num_frames*self.reader.channels)
      return (output, len(output) == num_frames * self.reader.channels)
   
   def play_toggle(self):
      self.playing = not self.playing

   def reset(self):
      self.reader.set_pos(0)

# let's make a class that holds a small amount of wave data in memory
# and can play that like a sample, almost like a note.
class WaveSnippet(object):
   def __init__(self, wave_reader, start_frame, num_frames) :
      super(WaveSnippet, self).__init__()

      # get a local copy of the audio data from WaveReader
      wave_reader.set_pos(start_frame)
      self.data = wave_reader.read(num_frames)

   # the WaveSnippet itself should not play the note. It is not a generator.
   # Just a place to hold data. We create a generator with a reference to the
   # data and a way of keeping track of the current frame. That way, we can
   # have a single source of data held in a data, but multiple play objects
   # (ie Generators) for playing the data
   class Generator(object):
      def __init__(self, data) :
         super(WaveSnippet.Generator, self).__init__()
         self.data = data
         self.frame = 0
         self.end = len (self.data)

      def generate(self, num_frames) :
         # grab correct chunk of data
         start = self.frame * 2
         end = (self.frame + num_frames) * 2
         output = self.data[start : end]

         # advance current-frame
         self.frame += num_frames

         # return
         return (output, len(output) == num_frames * 2)

   # to play this audio, we need a helper function to create
   # the generator (this is known as a Factory Function)
   def make_generator(self) :
      return WaveSnippet.Generator(self.data)
      

class AudioRegion(object):
   def __init__(self):
      super(AudioRegion, self).__init__()
      # TODO finish implementation


class SongRegions(object):
   def __init__(self, filepath):
      super(SongRegions, self).__init__()

      self.regions = []
      # TODO - finish implementation


def make_snippits(regions):
   pass
   # TODO - should return a dictionary of snippets

