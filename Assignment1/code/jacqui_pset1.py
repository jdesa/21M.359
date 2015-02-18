# To help you get going, this template has the main structures set up. You need
# to fill in the code according to Assignment 1.

import pyaudio
import numpy as np

import sys
sys.path.append('./common')
from core import *

kSamplingRate = 44100

#Every note and its 
keydict = {"cflat": 12, "c":0, "csharp":1, "dflat": 1, "d": 2, "dsharp":3, "eflat":3, "e":4, "esharp": 5, "fflat":5, "f":6, "fsharp":7, "gflat":7, "g":8, "gsharp":9, "aflat":9, "a": 10, "asharp":11, "bflat":11, "b":12, "bsharp":0}

def pitch_to_frequency(pitch):
   A4_pitch = 69
   A4_freq = 440
   pitchdif = pitch - A4_pitch
   return A4_freq*((2)**(1.0/12))**pitchdif
   
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
      self.rootpitch = 60 #Pitch of the root of the current key

   ############################
   ###  Extra Functions
   ############################   

   def set_key(self, newkey):
      rootpitch = keydict[newkey] 
      newrootpitch = rootpitch + 12*(self.octave + 1)
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
      self.wavetype = wavetype
      for generator in self.generatorlist:
         generator.set_wavetype(wavetype)

   ############################
   ### Generator Functions
   ############################   
   
   def add_generator(self, gen):
      if gen not in self.generatorlist:
         #Make sure a new note isn't added while another decays
         self.generatorlist.append(gen)

   def remove_generator(self, gen):
      for generator in self.generatorlist:
         if generator == gen:
            self.generatorlist.remove(generator)

   def release_generator(self, gen):
      for generator in self.generatorlist:
         if generator == gen:
            #Switch note from attack to decay mode
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
      ones_array = np.ones(frame_count, dtype = np.float32)
      total_envelope = np.zeros(frame_count, dtype = np.float32)
      brokengens = []
      for generator in self.generatorlist:
         (genoutput, continueflag, envelope) = generator.generate(frame_count)
         if continueflag == True: 
            output += genoutput
            total_envelope += envelope
         else:
            brokengens.append(generator)
            
      for generator in brokengens:
         self.remove_generator(generator)

      output = np.divide(output*self.gain, 1.0+total_envelope)
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
      self.attack_param = 0.1
      self.attack_slope = 2.
      self.decay_param = .1
      self.decay_slope = 2.
      self.decay_start_frame = 0 
      self.decayframes = 0 #Keeps track of number of frames since decay mode began
      
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
      envelope = self.generate_attack_envelope(audioarray) if self.attack_status else self.generate_decay_envelope(audioarray)
      enveloped_wave = np.multiply(envelope,overtone_wave)
      self.frames += frames
      note_ongoing = True if self.attack_status else (self.decayframes < self.decay_param*kSamplingRate) 
      #Note is always ongoing while in attack status (while the button is pressed) and ends after the decay time ends.
      return (enveloped_wave, note_ongoing, envelope)

   def generate_overtone(self, frames):
      overtone_output = np.zeros(frames)
      wave_series = self.wavetypes[self.wavetype]
      for harmonic in range(len(wave_series)):
         audioarray = np.arange(self.frames, self.frames + frames)
         factor = harmonic * self.freq * 2.0 * np.pi / float(kSamplingRate)
         output = wave_series[harmonic]*np.sin(factor*audioarray, dtype = 'float32')
         overtone_output += output
      overtone_output = overtone_output/np.sum(wave_series)
      return overtone_output

   def generate_decay_envelope(self, audioarray):
      maximum_decay = np.ones(len(audioarray))
      envelope = 1.0 - np.minimum(maximum_decay,((audioarray - self.decay_start_frame)/float(self.decay_param*kSamplingRate))**float(1.0/self.decay_slope)) 
      self.decayframes += len(audioarray)
      return envelope

   def generate_attack_envelope(self,audioarray):
      maximum_attack = np.ones(len(audioarray))
      envelope = np.minimum(maximum_attack,(audioarray/float(self.attack_param*kSamplingRate))**float(1.0/self.attack_slope)) 
      return envelope

####################
## Main Widget     
####################

majorkeyintervals = [0, 2, 4, 5, 7, 9, 11, 12]
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
      except:
         if keycode[1] == '[' or keycode[1] == ']':
            self.keymodifier = ""

run(MainWidget)
