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
      self.gain = .5
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

      
   def add_generator(self, gen):
      self.generatorlist.append(gen)

   def remove_generator(self, gen):
      for generator in self.generatorlist:
         if generator == gen:
            generator.set_attack_status(False)

   def get_generators(self):
      for generator in self.generatorlist:
         print generator.getName()

   def set_gain(self, gain) :
      self.gain = gain

   def get_gain(self) :
      return self.gain

   def _callback(self, in_data, frame_count, time_info, status):
      output = np.zeros(frame_count, dtype = np.float32)
      for generator in self.generatorlist:
         (genoutput, continueflag) = generator.generate(frame_count)
         if continueflag == True: 
            output += genoutput
         else:
            brokengenerators = []
            brokengenerators.append(generator)
            for generator in brokengenerators:
               self.generatorlist.remove(generator)
      output = output*self.gain/len(self.generatorlist)
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
         return None

      cnt = self.audio.get_device_count()
      for i in range(cnt):
         dev = self.audio.get_device_info_by_index(i)
         if dev['hostApi'] == host_api_idx:
            print 'Found Device', i
            return i

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
   def __init__(self,pitch,dur):
      self.freq = pitch_to_frequency(pitch)
      self.dur = dur
      self.frames = 0

      self.attack_status = True
      self.attack_param = dur
      self.attack_slope = 2.
      self.decay_param = .6
      self.decay_slope = 2.

      self.wavetypes = {}
      self.wavetypes["sine"] = [0, 1]
      self.wavetypes["sqr"] = [0, 1, 0, 1/3., 0, 1/5., 0, 1/7., 0, 1/9., 0, 1/11., 0, 1/13., 0, 1/15., 0, 1/17.]
      self.wavetypes["tri"] = [0, 1, 0, 1/9., 0, 1/25., 0, 1/49., 0, 1/81., 0, 1/121.,0,1/169.,0,1/225.,0,1/289.]
      self.wavetypes["saw"] = [0,1, 0,1/2., 0, 1/3., 0, 1/4., 0, 1/5., 0, 1/6., 0, 1/7., 0, 1/8., 0, 1/9.]   
      self.wavetype = "sine"

   def __eq__ (self, other):
      return (other.freq == self.freq and other.dur == self.dur) 
   
   ############################
   ### Setter/Getter Functions
   ############################

   def set_attack_status(self, attack_status):
      self.attack_status = attack_status
   
   def set_attack_param(self, attack_param):
      self.attack_param = float(attack_param)

   def set_attack_slope(self, attack_slope):
      self.attack_slope = float(attack_slope)

   def set_decay_param(self, decay_param):
      self.decay_param = float(decay_param)

   def set_decay_slope(self, decay_slope):
      self.decay_slope = float(decay_slope)

   def set_wavetype(self, wavetype):
      #Ensures that the wavetype is valid.
      if wavetype in self.wavetypes: 
         self.wavetype = wavetype

   def getName(self):
      return "NoteGenerator with freq " + str(self.freq) + " and dur " + str(self.dur)

   ##########################
   ### Generation Functions
   ##########################

   def generate(self, frames):
      audioarray = np.arange(self.frames, self.frames + frames)
      overtone_wave = self.generate_overtone(frames)
      envalope = self.generate_attack_envalope(audioarray) if self.attack_status else self.generate_decay_envalope(audioarray)
      envaloped_wave = np.multiply(envalope,overtone_wave)
      self.frames += frames
      note_ongoing = self.frames < (self.dur+self.decay_param)*kSamplingRate
      return (envaloped_wave, note_ongoing)

   def generate_overtone(self, frames):
      finaloutput = np.zeros(frames)
      wave_series = self.wavetypes[self.wavetype]
      for i in range(len(wave_series)):
         audioarray = np.arange(self.frames, self.frames + frames)
         factor = i * self.freq * 2.0 * np.pi / float(kSamplingRate )
         output = wave_series[i]*np.sin(factor*audioarray, dtype = 'float32')
         finaloutput += output
      return finaloutput

   def generate_decay_envalope(self, audioarray):
      env = 1.0 - (audioarray/float(self.decay_param*kSamplingRate))**float(1.0/self.decay_slope) 
      return env

   def generate_attack_envalope(self,audioarray):
      env = (audioarray/float(self.attack_param*kSamplingRate))**float(1.0/self.attack_slope) 
      return env

def pitch_to_frequency(pitch):
   Apitch = 69
   pitchdif = pitch - Apitch
   return 440*((2)**(1.0/12))**pitchdif

class MainWidget(BaseWidget):
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      print self.audio.get_generators()

   def on_key_down(self, keycode, modifiers):
      print 'key-down', keycode, modifiers
      if keycode[1] == '1':
         newgen_C = NoteGenerator(60, 5)
         self.audio.add_generator(newgen_C) 
         print "Added generator 1"
         print self.audio.get_generators()

      elif keycode[1] == '2':
         newgen_E = NoteGenerator(64, 10)
         self.audio.add_generator(newgen_E)  
         print "Added generator 2"
         print self.audio.get_generators()
            
      elif keycode[1] == '3':
         newgen_G = NoteGenerator(67, 5)
         self.audio.add_generator(newgen_G)  
         print "Added generator 3"
         print self.audio.get_generators()

   def on_key_up(self, keycode):
      # Your code here. You can change this whole function as you wish.
      print 'key up', keycode
      if keycode[1] == '1':
         newgen_C = NoteGenerator(60, 5)
         self.audio.remove_generator(newgen_C) 

      elif keycode[1] == '2':
         newgen_E = NoteGenerator(64, 10)
         self.audio.remove_generator(newgen_E)  
            
      elif keycode[1] == '3':
         newgen_G = NoteGenerator(67, 5)
         self.audio.remove_generator(newgen_G)   

run(MainWidget)
