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
      self.frames = 0

   def generate(self, num_frames) :
      if self.playing:
         output = self.reader.read(num_frames)
         self.frames += num_frames
      else:
         output = np.zeros(num_frames*self.reader.channels)
      return (output, len(output) == num_frames * self.reader.channels)
   
   def play_toggle(self):
      self.playing = not self.playing

   def reset(self):
      self.reader.set_pos(0)
      self.frames = 0
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

   # the WaveSnippet itself should not play the note. It is not a generator.
   # Just a place to hold data. We create a generator with a reference to the
   # data and a way of keeping track of the current frame. That way, we can
   # have a single source of data held in a data, but multiple play objects
   # (ie Generators) for playing the data
   class Generator(object):
      def __init__(self, data, loop_on, speed = 1.0) :
         super(WaveSnippet.Generator, self).__init__()
         self.speed = 1.0
         self.data = data
         self.interpdata = self.shift_data()
         self.loop_on = True
         self.playing = True
         self.frame  = 0
         self.end = len(self.data)/self.speed

      def shift_data(self):
         '''
         #Original Interp Method
         original_x = np.arange(0, len(self.data), 1.0, dtype = np.float32)
         shifted_x = np.arange(0, len(self.data), self.speed, dtype=np.float32)
         interpdata = np.interp(shifted_x, original_x, self.data)
         self.end = len(self.data)/self.speed
         return interpdata
         '''
         
         #Code for Correct Shifting Model:         
         interpdata = np.arange(0, len(self.data), self.speed, dtype=np.float32)

         original_x_left = np.arange(0, len(self.data)/2.0, 1.0, dtype = np.float32)
         shifted_x_left = np.arange(0, len(self.data)/2.0, self.speed, dtype=np.float32)
         interpdata_left = np.interp(shifted_x_left, original_x_left, self.data[0::2])

         original_x_right = np.arange(0, len(self.data)/2.0, 1.0, dtype = np.float32)
         shifted_x_right = np.arange(0, len(self.data)/2.0, self.speed, dtype=np.float32)
         interpdata_right = np.interp(shifted_x_right, original_x_right, self.data[1::2])

         interpdata[0::2] = interpdata_left
         #Dealing with edge cases relating to the length of the interpolated right channel (whether interpdata is of even or odd length)
         if len(interpdata[1::2]) == len(interpdata_right):
            interpdata[1::2] = interpdata_right
         elif (len(interpdata[1::2]) == len(interpdata_right)+1):
            interpdata_right.append(interpdata_right[-1]) #Add a copy of the very last sample
            interpdata[1::2] = interpdata_right
         elif len(interpdata[1::2]) == len(interpdata_right)-1:
            interpdata[1::2] = interpdata_right[0:len(interpdata_right)-1]

         self.end = len(self.data)/self.speed
         return interpdata         

      def generate(self, num_frames):
         start = (self.frame * 2)
         end = (self.frame + num_frames) * 2
         output = self.interpdata[start : end]
         self.frame += num_frames
         
         #Looping case
         if (end > self.end):
            if self.loop_on:
               wrapframes = num_frames - (end-self.end) 
               #Use remaining frames and a subsection of frames from the start
               output = np.concatenate([output[start:self.end],output[0:wrapframes]])
               self.frame = wrapframes
               end = 0
            else:
               output = output*self.decay_envelope(len(output))

         continuecondition = True if end <= self.end else False
         
         if not self.playing:
            output = output*0

         return (output, continuecondition)
      
      def stop_generator(self):
         self.loop_on = False
         self.playing = False

      def start_generator(self):
         self.playing = True

      def inc_speed(self):
         self.speed = self.speed*2.0**(1.0/12.0)
         self.interpdata = self.shift_data()

      def dec_speed(self):
         self.speed = self.speed/(2.0**(1.0/12.0))
         self.interpdata = self.shift_data()

      def decay_envelope(self, num_frames):
         audioarray = np.arange(0, num_frames)
         envelope = np.clip(1.0 - audioarray/(float(num_frames)**float(1.0/2.0)), 0.0, 1.0) 
         return envelope

      def attack_envelope(self, num_frames):
         audioarray = np.arange(0, num_frames)
         envelope = np.clip(audioarray/(float(num_frames)**float(1.0/2.0)), 0.0, 1.0) 
         return envelope
         
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

         regions.append(AudioRegion(counter, start_frame, num_frames))
      return regions

