
import numpy as np
import matplotlib.pyplot as plt

x0 = np.linspace(0.0, 1.0, 200)
x1 = np.linspace(0.0, 1.0, 16)
x2 = np.linspace(0.0, 16/19., 16)
x2n = np.linspace(0.0, 1.0, 16)

y0 = np.cos(2 * np.pi * x0)
y1 = np.cos(2 * np.pi * x1)
y2 = np.cos(2 * np.pi * x2)

plt.subplot(3, 1, 1)
plt.plot(x0, y0)
plt.stem(x1, y1)
plt.title('Original')

plt.subplot(3, 1, 2)
plt.stem(x1, y1)
plt.stem(x2, y2, 'r', 'ro')
plt.title('Resampling at T1 = 1.19 T0')

plt.subplot(3, 1, 3)
plt.plot(x2n, y2, 'r')
plt.stem(x2n, y2, 'r', 'ro')
plt.title('Playback')

plt.show()
