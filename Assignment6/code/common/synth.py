#####################################################################
#
# synth.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
import fluidsynth

# create another kind of generator that generates audio based on the fluid
# synth synthesizer
class Synth(fluidsynth.Synth):
   def __init__(self, filepath, gain = 0.8):
      super(Synth, self).__init__(gain)
      self.sfid = self.sfload(filepath)
      if self.sfid == -1:
         raise Exception('Error in fluidsynth.sfload(): cannot open ' + filepath)
      self.program(0, 0, 0)

   def program(self, ch, bank, preset):
      self.program_select(ch, self.sfid, bank, preset)

   def generate(self, num_frames):
      # get_samples() returns interleaved stereo, so all we have to do is scale
      # the data to [-1, 1].
      samples = self.get_samples(num_frames).astype(np.float32) 
      samples *= (1.0/32768.0)
      return (samples, True)
