Go to: https://drive.google.com/folderview?id=0B2elrq8YD1jxbWxnMlo2bnV4eUU&usp=sharing

Mac install: 
- download Synapse-Mac.zip.
- Plug in Kinect
- Run Synapse

PC install (win7 only): 
- Do NOT plug in your Kinect yet.
- Download OpenNI_NITE_Installer-win32-0.27.zip.
- Unpack the zip file and run the four installers IN ORDER. The order of installation is critical.
- Now plug in your Kinect. Plug-n-play will automatically download and setup drivers. This might take a while (5 minutes)
- Download Synapse-Win.zip. 
- Run Synapse

To read more about Synapse: http://synapsekinect.tumblr.com/


Normally, you would run Synapse and Kivy on the same machine. However, if this doesn't work for you, you can run Synapse on one machine and Kivy on the other.

To run Synapse on one machine and Kivy on another machine:
- Find the IP address of both machines. You can do this via:
- $ kivy oscbridge.py (NOTE the version of pyOSC we are using has been already added to your Kivy environment. oscbridge.py will not work from a non-kivy-based python)
- On the Synapse Machine:
  - Run Synapse
  - $ kivy oscbridge.py <IP-of-Kivy-machine>

- On the Kivy Machine:
  - $ kivy lecture6.py <N> <IP-of-Synapse-machine>
  (N is the Widget number to test)

