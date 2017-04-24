# import pyaudio
# import time
# import numpy as np
# import scipy.signal as signal
# from findfundfreq import *
import matplotlib.pyplot as plt

"""
Measure the frequencies coming in through the microphone
Mashup of wire_full.py from pyaudio tests and spectrum.py from Chaco examples
"""

import pyaudio
import numpy as np
import scipy.signal
from findfundfreq import *

CHUNK = 1024*2

WIDTH = 2
DTYPE = np.int16
MAX_INT = 32768.0

CHANNELS = 1
RATE = 11025*1
RECORD_SECONDS = 3


p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                frames_per_buffer=CHUNK)

print("* recording")



for i in np.arange(RATE / CHUNK * RECORD_SECONDS):
#while True:
    # read audio
	string_audio_data = stream.read(CHUNK)
	audio_data = np.fromstring(string_audio_data, dtype=DTYPE)
	normalized_data = audio_data / MAX_INT
	freq = findfundfreq(normalized_data, RATE, False)
	print(freq)

plt.plot(audio_data)
plt.show()

print("* done")

stream.stop_stream()
stream.close()

p.terminate()