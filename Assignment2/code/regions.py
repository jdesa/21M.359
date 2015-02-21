import numpy as np
import wave
from audio import kSamplingRate
from wavegen import *

class AudioRegion:
	def __init__(self, name, startframe, numframes):
		self.name = name
		self.startframe = startframe
		self.numframes = numframes #Same as length

class SongRegions:
	def __init__(self):
		self.songregions = []

		f = open('hideandseek16_regions.txt')
		counter = 0
		for line in iter(f):
			counter = counter+1 #Keeping track for the name
		    
		    words = line.split()
		    starttime = words[0] 
		    endtime = words[1]
		    
		    startframe = starttime*kSamplingRate
		    endframe = endtime*kSamplingRate
		    numframes = endtime - startframe
		    
		    print (startframe, numframes)
		    self.songregions.append(AudioRegion(counter, startframe, numframes))
		f.close()

class WaveSnippets:
	def __init__(self, SongRegion):
		snippets = {}
		for audioregion in SongRegion.songregions:
			snippets[audioregion.name] = 

