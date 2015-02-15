# To help you get going, this template has the main structures set up. You need
# to fill in the code according to Assignment 1.

import pyaudio
import numpy as np

import sys
sys.path.append('./common')
from core import *

kSamplingRate = 44100

class Audio:
   def __init__(self):
      self.generatorlist = []
      self.audio = pyaudio.PyAudio()
      dev_idx = self._find_best_output()
      self.stream = self.audio.open(format = pyaudio.paFloat32,
         channels = 1,
         frames_per_buffer = 512,
         rate = kSamplingRate,
         output = True,
         input = False,
         output_device_index = dev_idx,
         stream_callback = self._callback)
      register_terminate_func(self.close)
      self.gain = .5
      # Your code here.
      

   def add_generator(self, gen):
      self.generatorlist.append(gen)      

   def set_gain(self, gain) :
   # Your code here.
      self.gain = np.clip(gain, 0, 1)
      print self.gain

   def get_gain(self) :
   # Your code here.
      return self.gain

   def _callback(self, in_data, frame_count, time_info, status):
      brokengenerators = []
      output = np.zeros(frame_count, dtype = float32)
      for generator in self.generatorlist:
         (genoutput, pyaudio.paContinue) = generator.generate(frame_count)
         if paContinue == True: 
            output += genoutput
         else:
            brokengenerators.append(generator)
            for generator in brokengenerators:
               self.generatorsList.remove(generator)
               output = output*self.gain
               return (output.tostring(), pyaudio.paContinue)

   # return the best output index if found. Otherwise, return None
   def _find_best_output(self):
      # for Windows, we want to find the ASIO host API and device
      cnt = self.audio.get_host_api_count()
      for i in range(cnt):
         api = self.audio.get_host_api_info_by_index(i)
         if api['type'] == pyaudio.paASIO:
            host_api_idx = i
            print 'Found ASIO', host_api_idx
            break
         else:
         # did not find desired API. Bail out
            return None

         cnt = self.audio.get_device_count()
         for i in range(cnt):
            dev = self.audio.get_device_info_by_index(i)
            if dev['hostApi'] == host_api_idx:
               print 'Found Device', i
               return i

      # did not find desired device.
      return None

   # shut down the audio driver. It is import to do this before python quits.
   # Otherwise, python might hang without fully shutting down. 
   # core.register_terminate_func (see __init__ above) will make sure this
   # function gets called automatically before shutdown.
   def close(self):
      self.stream.stop_stream()
      self.stream.close()
      self.audio.terminate()



class NoteGenerator(object):

   def __init__(freq, dur):
      self.freq = freq
      self.dur = dur
      self.frames = 0

   def generate(self, frames):
      audioarray = np.arange(self.frame, self.frame + frames)
      factor = self.frequency * 2.0 * np.pi / kSamplingRate 
      output = np.sin(factor * frames, dtype = 'float32')
      self.frame += frames
      return (output, pyaudio.paContinue)


def pitch_to_frequency(pitch):
# Your code here.
pass

class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()      
      self.audio = Audio()


class MainWidget(BaseWidget) :
   def __init__(self):
      super(MainWidget, self).__init__()

      self.audio = Audio()

   def on_key_down(self, keycode, modifiers):
      # Your code here. You can change this whole function as you wish.
      print 'key-down', keycode, modifiers

      if keycode[1] == '1':
         pass

      elif keycode[1] == 'up':
         pass

      elif keycode[1] == 'down':
         pass

   def on_key_up(self, keycode):
   # Your code here. You can change this whole function as you wish.
      print 'key up', keycode

run(MainWidget1)
