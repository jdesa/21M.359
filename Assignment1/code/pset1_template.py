# To help you get going, this template has the main structures set up. You need
# to fill in the code according to Assignment 1.

import pyaudio
import numpy as np

import sys
sys.path.append('./common')
from core import *

kSamplingRate = 44100
keydict = {"cflat": 12, "c":0, "csharp":1, "dflat": 1, "d": 2, "dsharp":3, "eflat":3, "e":4, "esharp": 5, "fflat":5, "f":6, "fsharp":7, "gflat":7, "g":8, "gsharp":9, "aflat":9, "a": 10, "asharp":11, "bflat":11, "b":12, "bsharp":0}

def pitch_to_frequency(pitch):
   Apitch = 69
   pitchdif = pitch - Apitch
   return 440*((2)**(1.0/12))**pitchdif
   
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

      self.wavetype = "sine"
      self.octave = 4
      self.rootpitch = 60 #MiddleC
      self.isminor = False

      #Dictionary showing the pitch locations of each key

   ############################
   ###  Extra Functions
   ############################   

   def set_key(self, newkey):
      baserootpitch = keydict[newkey]
      newrootpitch = baserootpitch + 12*(self.octave + 1)
      self.change_generator_pitches(newrootpitch)
      self.rootpitch = newrootpitch

   def set_octave(self, newoctave):
      newrootpitch = (self.rootpitch)%12 + 12*(newoctave+1)
      self.change_generator_pitches(newrootpitch)
      self.rootpitch = newrootpitch
      self.octave = newoctave

   def change_generator_pitches(self, newrootpitch):
      rootpitchdiff = newrootpitch - self.rootpitch
      for generator in self.generatorlist:
         generator.change_pitch(rootpitchdiff)

   def set_wavetype(self, wavetype):
      print "changing wavetype at audio level"
      self.wavetype = wavetype
      for generator in self.generatorlist:
         print "in for loop"
         generator.set_wavetype(wavetype)

   def change_to_minor(self, isminor):
      self.isminor = isminor

   ############################
   ### Generator Functions
   ############################   
   
   def add_generator(self, gen):
      self.generatorlist.append(gen)

   def remove_generator(self, gen):
      for generator in self.generatorlist:
         if generator == gen:
            self.generatorlist.remove(generator)

   def release_generator(self, gen):
      for generator in self.generatorlist:
         if generator == gen:
            generator.set_attack_status(False)
            generator.set_decay_frame()

   def set_gain(self, gain) :
      self.gain = gain

   def get_gain(self) :
      return self.gain

   def print_generators(self):
      for generator in self.generatorlist:
         print generator.getName()

   def _callback(self, in_data, frame_count, time_info, status):
      output = np.zeros(frame_count, dtype = np.float32)
      for generator in self.generatorlist:
         (genoutput, continueflag) = generator.generate(frame_count)
         if continueflag == True: 
            output += genoutput
         else:
            self.remove_generator(generator)
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
   def __init__(self,pitch,wavetype):
      self.pitch = pitch
      self.freq = pitch_to_frequency(pitch)
      self.frames = 0

      self.attack_status = True
      self.attack_param = 0.01
      self.attack_slope = 2.
      self.decay_param = .2
      self.decay_slope = 2.
      self.decayframes = 0
      self.decay_start_frame = 0 

      self.wavetypes = {}
      self.wavetypes["sine"] = [0, 1]
      self.wavetypes["sqr"] = [0, 1, 0, 1/3., 0, 1/5., 0, 1/7., 0, 1/9., 0, 1/11., 0, 1/13., 0, 1/15., 0, 1/17.]
      self.wavetypes["tri"] = [0, 1, 0, 1/9., 0, 1/25., 0, 1/49., 0, 1/81., 0, 1/121.,0,1/169.,0,1/225.,0,1/289.]
      self.wavetypes["saw"] = [0,1, 0,1/2., 0, 1/3., 0, 1/4., 0, 1/5., 0, 1/6., 0, 1/7., 0, 1/8., 0, 1/9.]   
      self.wavetype = wavetype

   def __eq__ (self, other):
      return (other.freq == self.freq) 
   
   ############################
   ### Setter/Getter Functions
   ############################

   def set_decay_frame(self):
      self.decay_start_frame = self.frames

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
      self.wavetype = wavetype
      print self.wavetype
      
   def getName(self):
      return "NoteGenerator with freq " + str(self.freq)

   ##########################
   ### Modifier Functions
   ##########################

   def change_pitch(self, pitchdiff):
      self.pitch += pitchdiff
      self.freq = pitch_to_frequency(self.pitch)

   ##########################
   ### Generation Functions
   ##########################
   def generate(self, frames):
      audioarray = np.arange(self.frames, self.frames + frames)
      overtone_wave = self.generate_overtone(frames)
      envalope = self.generate_attack_envalope(audioarray) if self.attack_status else self.generate_decay_envalope(audioarray)
      envaloped_wave = np.multiply(envalope,overtone_wave)
      self.frames += frames
      note_ongoing = True if self.attack_status else (self.decayframes < self.decay_param*kSamplingRate)
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
      maximum_decay = np.ones(len(audioarray))
      env = 1.0 - np.minimum(maximum_decay,((audioarray - self.decay_start_frame)/float(self.decay_param*kSamplingRate))**float(1.0/self.decay_slope)) 
      self.decayframes += len(audioarray)
      return env

   def generate_attack_envalope(self,audioarray):
      maximum_attack = np.ones(len(audioarray))
      env = np.minimum(maximum_attack,(audioarray/float(self.attack_param*kSamplingRate))**float(1.0/self.attack_slope)) 
      return env

####################
## Main Widget     
####################

majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]
#minorkeyintervals = [0, 2, 3, 5, 7, 8, 10, 12]

class MainWidget(BaseWidget):
   def __init__(self):
      super(MainWidget, self).__init__()
      self.audio = Audio()
      self.keymodifier = ""

   def on_key_down(self, keycode, modifiers):
      print 'key-down', keycode, modifiers
      
      #Setting changed keys as Sharp or Flat
      if keycode[1] == '[':
         self.keymodifier = "flat"
      elif keycode[1] == ']':
         self.keymodifier = "sharp"
      
      try:
         #Adding more notes within a scale
         scaledegree = int(keycode[1])
         print "wavetype is: " + self.audio.wavetype
         if scaledegree in range(1,9): #valid scale degrees -- in base 1
            self.audio.add_generator(NoteGenerator((self.audio.rootpitch + majorkeyintervals[scaledegree-1]), self.audio.wavetype))
      except:
         #Changing key
         if keycode[1] in ["a", "b", "c", "d", "e", "f", "g"]:
            self.audio.set_key(keycode[1]+self.keymodifier)
         #Changing wavetype
         elif keycode[1] == "m":
            self.audio.set_wavetype("sine")
         elif keycode[1] == ",":
            self.audio.set_wavetype("tri")
         elif keycode[1] == ".":
            self.audio.set_wavetype("sqr")
         elif keycode[1] == "/":
            self.audio.set_wavetype("saw")
         #Changing octave
         elif keycode[1] == "o":
            if self.audio.octave - 1 >= 0:
               self.audio.set_octave(self.audio.octave - 1)
         elif keycode[1] == "p":
            self.audio.set_octave(self.audio.octave + 1)

   def on_key_up(self, keycode):
      # Your code here. You can change this whole function as you wish.
      print 'key up', keycode
      try:
         scaledegree = int(keycode[1])
         if scaledegree in range(1,9): #valid scale degrees -- in base 1
            self.audio.release_generator(NoteGenerator((self.audio.rootpitch + majorkeyintervals[scaledegree-1]), self.audio.wavetype))
            print self.audio.wavetype
      except:
         if keycode[1] == '[' or keycode[1] == ']':
            self.keymodifier = ""

run(MainWidget)
