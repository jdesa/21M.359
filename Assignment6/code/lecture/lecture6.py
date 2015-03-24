#lecture6.py

# common import
import sys
sys.path.append('../common')
from core import *
from kinect import *
from graphics import *

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup

import numpy as np

# if this is set, assume Kinect/Synapse is running on a remote machine
# and send/receive from that ip address
kinect_remote_ip = None

# get basic Kinect module working - showing data from right-hand position
class MainWidget1(BaseWidget) :
   def __init__(self):
      super(MainWidget1, self).__init__()

      # and text to display our status      
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.kinect = Kinect(kinect_remote_ip)
      self.kinect.add_joint(kJointRightHand)

   def on_update(self) :
      self.kinect.on_update()
      pt = self.kinect.get_joint(kJointRightHand)
      self.label.text = '\n'.join([str(x) for x in pt])



# show a single hand graphically
class MainWidget2(BaseWidget) :
   def __init__(self):
      super(MainWidget2, self).__init__()

      # and text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.kinect = Kinect(kinect_remote_ip)
      self.kinect.add_joint(kJointRightHand)

      self.right_hand = Cursor3D((400,300), (10, 10), (.2, .6, .2), True)
      self.canvas.add(self.right_hand)

   def on_update(self) :
      self.kinect.on_update()

      pt = self.kinect.get_joint(kJointRightHand)
      pt_min = np.array([-250.0, -200, 0])
      pt_max = np.array([700.0, 700, -500])
      norm_pt = scale_point(pt, pt_min, pt_max)

      self.label.text = '\n'.join(['%.0f %.2f' % x for x in zip(pt, norm_pt)])

      self.right_hand.set_pos(norm_pt)


# Show 4 different skeletal joings - two hands, two knees
class MainWidget3(BaseWidget) :
   def __init__(self):
      super(MainWidget3, self).__init__()

      # and text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.kinect = Kinect(kinect_remote_ip)
      self.kinect.add_joint(kJointRightHand)
      self.kinect.add_joint(kJointLeftHand)
      self.kinect.add_joint(kJointRightKnee)
      self.kinect.add_joint(kJointLeftKnee)

      self.right_hand = Cursor3D((400,300), (10, 10), (.2, .6, .2), True)
      self.canvas.add(self.right_hand)

      self.left_hand = Cursor3D((400,300), (10, 10), (.2, .2, .6), True)
      self.canvas.add(self.left_hand)

      self.right_knee = Cursor3D((400,300), (10, 10), (.7, .6, .2), True)
      self.canvas.add(self.right_knee)

      self.left_knee = Cursor3D((400,300), (10, 10), (.7, .2, .6), True)
      self.canvas.add(self.left_knee)

   def on_update(self) :
      self.kinect.on_update()

      right_hand_pt = self.kinect.get_joint(kJointRightHand)
      left_hand_pt = self.kinect.get_joint(kJointLeftHand)
      right_knee_pt = self.kinect.get_joint(kJointRightKnee)
      left_knee_pt = self.kinect.get_joint(kJointLeftKnee)

      pt_min = np.array([-1000.0, -1000, 0])
      pt_max = np.array([1000.0, 1000, -1000])

      right_hand_norm = scale_point(right_hand_pt, pt_min, pt_max)
      left_hand_norm = scale_point(left_hand_pt, pt_min, pt_max)
      right_knee_norm = scale_point(right_knee_pt, pt_min, pt_max)
      left_knee_norm = scale_point(left_knee_pt, pt_min, pt_max)

      self.label.text = '\n'.join(['%.0f' % x for x in np.append(right_hand_pt, left_hand_pt)])

      self.right_hand.set_pos(right_hand_norm)
      self.left_hand.set_pos(left_hand_norm)
      self.right_knee.set_pos(right_knee_norm)
      self.left_knee.set_pos(left_knee_norm)


# A clap gesture detector. Notifies a callback when a clap is detected.
# the callback function takes a single argument: pos (3D point)
class ClapGesture(object):
   def __init__(self, kinect, callback):
      super(ClapGesture, self).__init__()
      self.kinect = kinect
      self.callback = callback
      
      # tunable parameters:
      self.min_dist = 100
      self.sep_dist = 200

      # runtime params:
      self.hands_apart = False

   def on_update(self):
      right_pt = self.kinect.get_joint(kJointRightHand)
      left_pt = self.kinect.get_joint(kJointLeftHand)

      dist = np.linalg.norm(right_pt - left_pt)

      if self.hands_apart and dist < self.min_dist:
         self.hands_apart = False

         # position of clap is the average position of the two hands
         pos = (right_pt + left_pt) / 2
         print 'Clap at', pos
         self.callback(pos)

      if not self.hands_apart and dist > self.sep_dist:
         print 'Hand Separate'
         self.hands_apart = True


# An animation / display to go along with the Clap Gesture
class Pop(InstructionGroup) :
   def __init__(self, pos):
      super(Pop, self).__init__()
      self.color = Color()
      self.circle = Ellipse()
      self.add(self.color)
      self.add(self.circle)

      # create keyframe animation: a frame is: [r g b a r x y]
      # and initialize graphics to time = 0
      self.anim = KFAnim([0, 0.5], ([1, 0, 0, 1, 30, pos[0], pos[1]], [1, 0, 0, 0, 60, pos[0], pos[1]])) 
      self.time = 0
      self.on_update(0)

   def _apply(self, values):
      #print values
      self.color.rgba = values[0:4]
      radius = values[4]
      self.circle.size = radius * 2, radius * 2
      self.circle.pos = values[5:7] - radius

   def on_update(self, dt):
      values = self.anim.eval(self.time)
      self._apply(values)
      self.time += dt

      return self.anim.is_active(self.time)


# Demonstrate the Clap Gesture: Tracks the 2 hands and displays the Pop objects
# when the hands clap
class MainWidget4(BaseWidget) :
   def __init__(self):
      super(MainWidget4, self).__init__()

      # and text to display our status
      self.label = Label(text = 'foo', pos = (50, 400), size = (150, 200), valign='top',
                         font_size='20sp')
      self.add_widget(self.label)

      self.kinect = Kinect(kinect_remote_ip)
      self.kinect.add_joint(kJointRightHand)
      self.kinect.add_joint(kJointLeftHand)

      self.right_hand = Cursor3D((400,300), (10, 10), (.2, .6, .2), True)
      self.canvas.add(self.right_hand)

      self.left_hand = Cursor3D((400,300), (10, 10), (.2, .2, .6), True)
      self.canvas.add(self.left_hand)

      # for scaling hand locations -> [0,1]
      # this scaling sets up a retangular box 2 meters wide, 2 meters tall, and 1 meter in depth
      # centered around the player's toroso
      self.pt_min = np.array([-1000.0, -1000, 0])
      self.pt_max = np.array([1000.0, 1000, -1000])

      self.scene = Scene()
      self.add_widget(self.scene)

      self.clap = ClapGesture(self.kinect, self.on_clap)


   def on_touch_down(self, touch) :
      pop = Pop(touch.pos)
      self.scene.add_object(pop)

   # scale a point from millimeters to [0-1] space
   def _scale_point(self, pt) :
      return scale_point(pt, self.pt_min, self.pt_max)

   def on_update(self) :
      self.kinect.on_update()
      self.clap.on_update()

      right_hand_pt = self.kinect.get_joint(kJointRightHand)
      left_hand_pt = self.kinect.get_joint(kJointLeftHand)

      right_hand_norm = self._scale_point(right_hand_pt)
      left_hand_norm = self._scale_point(left_hand_pt)

      self.label.text = '\n'.join(['%.0f' % x for x in np.append(right_hand_pt, left_hand_pt)])

      self.right_hand.set_pos(right_hand_norm)
      self.left_hand.set_pos(left_hand_norm)

      self.scene.on_update()

   def on_clap(self, pos):
      pos = self._scale_point(pos)[0:2] * np.array([400, 300]) + np.array([10,10])
      pop = Pop(pos)
      self.scene.add_object(pop)


# convert pt into unit scale (ie, range [0,1]) assuming that pt falls in the
# the range [min_val, max_val]
# value is clipped [0,1]
def scale_point(pt, min_val, max_val):
   pt = (pt - np.array(min_val)) / (np.array(max_val) - np.array(min_val))
   pt = np.clip(pt, 0, 1)
   return pt


kinect_remote_ip
if len(sys.argv) < 2:
   print 'Specifiy which MainWidget to run'
   sys.exit()
elif len(sys.argv) >=3:
   kinect_remote_ip = sys.argv[2]
   print 'Using %s as IP address for machine running Synapse' % kinect_remote_ip

# pass in which MainWidget to run as a command-line arg
run(eval('MainWidget' + sys.argv[1]))
