#chord.py
import re

class Chord(object):
   def __init__(self, string):
      super(Chord, self).__init__()
      # root and quality will define the type of chord.
      # for example, D minor would be: root = 2, quality = [0, 3, 7]
      # quality should be sorted smallest to largest.
      self.root = 0
      self.quality = ""
      self.pitch_classes = []
      self.qualitydict = {
      "": [0, 4, 7],
      "M":[0, 4, 7],
      "m":[0, 3, 7],
      "m7":[0, 3, 7, 10],
      "7": [0, 4, 7, 10], 
      "M7": [0, 4, 7, 11],
      "dim": [0, 3, 6],
      "aug": [0, 4, 8],
      "sus": [0, 5, 7]
      }
      self.pitchdict = {
      "C":0,
      "C#":1,
      "Db":1,
      "D":2,
      "D#":3,
      "Eb":3,
      "E":4,
      "F":5,
      "F#":6,
      "Gb":6,
      "G":7,
      "G#":8,
      "Ab":8,
      "A":9,
      "A#":10,
      "Bb":10,
      "B":11,
      "B#":0
      }


      self._set_from_string(string)


   def __str__(self):
      return "Root is: " + str(self.root) + " Quality is: " + str(self.quality) + " Pitch classes are: " + str(self.pitch_classes)


   def _set_from_string(self, string):
      root_name = re.search(r"[ABCDEFG][#b]?", string).group(0)
      self.root = self.pitchdict[root_name]
      quality_string_split = string.split(root_name)
      if len(quality_string_split) > 1:
         quality_string = quality_string_split[1]
         for chordtype in self.qualitydict.keys():
            if quality_string == chordtype:
               self.quality = quality_string
               self.pitch_classes = self.qualitydict[self.quality]

   def get_quality(self):
      return self.quality

   def get_root(self):
      return self.root

   # returns the pitch classes for this chord, as derived from root and quality.
   # The returned list should be sorted small->large. For example,
   # D-minor-7 should return [0, 2, 5, 9]
   def get_pitch_classes(self):
      return self.pitch_classes      

class ChordMap(object):
   def __init__(self, chordfilepath):
      super(ChordMap, self).__init__()

      self.chordfilepath = chordfilepath




      # define the list of time-based chords here
      self.chords = self.parse_text_file(self.chordfilepath) # change to the container of your choice.

   # return the appropriate chord for the given beat
   def get_chord_at(self, beat):
      for i in range(len(self.chords) - 1):
         if self.chords[i][0] < beat and self.chords[i+1][0] >= beat:
            return self.chords[i][1]

   def parse_text_file(self, textfilepath):
      chords = []
      f = open(textfilepath)
      for line in iter(f):
         words = line.split()
         beatnum = int(words[0])
         chord = words[1]
         chords.append((beatnum, Chord(chord)))
      return chords


# write some of your tests here. They will not be run when this
# file is imported as a module
if __name__ == '__main__':
   print 'Running some tests on Chord and ChordMap'

   #print Chord("C")
   '''
   print "C: " + str(Chord("C"))
   print "Gm: " + str(Chord("Gm"))
   print "Eb7: " + str(Chord("Eb7"))
   print "Am7: " + str(Chord("Am7"))
   print "D#sus: " + str(Chord("D#sus"))
   '''

   chordmap =  ChordMap("_chords.txt")
   print "Chordmap at 10 " + str(chordmap.get_chord_at(10))

