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
      self.playing = False

# let's make a class that holds a small amount of wave data in memory
# and can play that like a sample, almost like a note.
class WaveSnippet(object):
   def __init__(self, wave_reader, start_frame, num_frames) :
      super(WaveSnippet, self).__init__()

      # get a local copy of the audio data from WaveReader
      wave_reader.set_pos(start_frame)
      self.data = wave_reader.read(num_frames)
      self.generator = None
      print self.generator

   # the WaveSnippet itself should not play the note. It is not a generator.
   # Just a place to hold data. We create a generator with a reference to the
   # data and a way of keeping track of the current frame. That way, we can
   # have a single source of data held in a data, but multiple play objects
   # (ie Generators) for playing the data
   class Generator(object):
      def __init__(self, data, loop_on, speed = 1.0) :
         super(WaveSnippet.Generator, self).__init__()
         self.speed = speed
         self.data = data
         self.interpdata = self.shift_data()
         self.end = len(self.interpdata)
         self.loop_on = True
         self.playing = True
         self.frame  = 0

      def shift_data(self):
         original_x = np.arange(0, len(self.data), 1.0)
         shifted_x = np.arange(0, len(self.data)*self.speed, self.speed)
         interpdata = np.interp(shifted_x, original_x, self.data)
         return interpdata

      def generate(self, num_frames):
         start = self.frame * 2
         end = (self.frame + num_frames) * 2
         output = self.data[start : end]
         print "loop on is: " + str(self.loop_on)
         print ("self.end " + str(self.end))
         print ("end is " + str(end))
         if (self.end < end + num_frames and self.loop_on):
            print "in loop case"
            self.frame = 0
            start = self.frame * 2
            end = (self.frame + num_frames) * 2
            output = self.interpdata[start : end]
         
         self.frame += num_frames
         return (output, len(output) == num_frames * 2)
      
      def stop_generator(self):
         self.loop_on = False
         self.playing = False

      def start_generator(self):
         self.playing = True

      def invert_loop(self):
         self.loop_on = not self.loop_on
         
   # to play this audio, we need a helper function to create
   # the generator (this is known as a Factory Function)
   def make_generator(self, loop_on, speed = 1.0):
      self.generator = WaveSnippet.Generator(self.data, loop_on, speed=1.0)
      return self.generator

class AudioRegion(object):
   def __init__(self, name, startframe, numframes):
      super(AudioRegion, self).__init__()
      self.name = name
      self.start_frame = startframe
      self.num_frames = numframes #Same as length


class SongRegions(object):
   def __init__(self, textfilepath, wavefilepath):
      super(SongRegions, self).__init__()
      self.textfilepath = textfilepath
      self.wavefilepath = wavefilepath
      self.reader = WaveReader(wavefilepath)
      self.regions = self.parse_text_file(textfilepath)

   def make_snippits(self):
      waveregions = {}
      for audioregion in self.regions:
         waveregions[str(audioregion.name)] = WaveSnippet(self.reader, audioregion.start_frame, audioregion.num_frames)
      print "waveregions: " + str(waveregions)
      return waveregions

   def parse_text_file(self, textfilepath):
      counter = 0
      regions = []
      f = open(textfilepath)
      for line in iter(f):
         counter = counter+1 #Keeping track for the name
          
         words = line.split()
         starttime = float(words[0])
         duration = float(words[2])

         start_frame = int(starttime*kSamplingRate)
         num_frames = int(duration*kSamplingRate)

         print "StartFrame: " + str(start_frame)
         print "Numframes: " + str(num_frames)
         regions.append(AudioRegion(counter, start_frame, num_frames))
      return regions
