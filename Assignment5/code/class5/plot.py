# show plotting tempo map:

import matplotlib.pyplot as plt
import numpy as np

from clock_lec import *

data = [(0,0), (4.0, kTicksPerQuarter*4), (8.0, kTicksPerQuarter*12), 
         (12.0, kTicksPerQuarter*14)]
tempo_map = TempoMap(data)

times = np.arange(0, 15, .01)
ticks = np.array([tempo_map.time_to_tick(x) for x in times])

plt.plot(times, ticks)
plt.show()
