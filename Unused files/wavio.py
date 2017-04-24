# wavio.py
# Author: Warren Weckesser
# License: BSD 3-Clause (http://opensource.org/licenses/BSD-3-Clause)
# Synopsis: A Python module for reading and writing 24 bit WAV files.
# Github: github.com/WarrenWeckesser/wavio

import wave as _wave
import numpy as _np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal

def main():
	rate, sampwidth, array = readwav('LowE.wav')
	print(rate)
	print(sampwidth)
	#for each in array:
	#	print(array[each])
	w = signal.hann(20)
	a = array.T[0] #get channel 1
	b=[(ele/2**16.)*2 for ele in a] #normalize data to be between -1 and 1
	corr = signal.correlate(b, b, mode='same')
	c = abs(fft(b)) # calculate fourier transform (note: the magnitude of the complex numbers)
	d = int(len(c)/2)  # half of the elements due to fft being symmetric
	print(d)
	
	fig, (ax_orig, ax_norm, ax_filt) = plt.subplots(3, 1, sharex=True)
	#fig, (ax_orig) = plt.subplots(1,1,sharex=True)
	ax_orig.set_title('signal in time')
	ax_orig.set_xlim([0,300000])
	ax_orig.set_ylim([-20000,20000])
	ax_orig.plot(a)
	
	ax_norm.set_title('normed signal')
	ax_norm.set_ylim([-1,1])
	ax_norm.plot(b)	

	ax_filt.set_title('filtered signal')
	ax_filt.set_ylim([-1000,1000])
	ax_filt.plot(corr)

	fig, (ax_fft) = plt.subplots(1,1)
	ax_fft.set_title('FFT of filtered signal')
	ax_fft.set_xlim([0,5000])
	ax_fft.set_ylim([0,200000])
	ax_fft.plot(abs(c[:(d-1)]))
	
	#fig.tight_layout()
	plt.show()
	
	return 0

def _wav2array(nchannels, sampwidth, data):
    """data must be the string containing the bytes from the wav file."""
    num_samples, remainder = divmod(len(data), sampwidth * nchannels)
    if remainder > 0:
        raise ValueError('The length of data is not a multiple of '
                         'sampwidth * num_channels.')
    if sampwidth > 4:
        raise ValueError("sampwidth must not be greater than 4.")

    if sampwidth == 3:
        a = _np.empty((num_samples, nchannels, 4), dtype=_np.uint8)
        raw_bytes = _np.fromstring(data, dtype=_np.uint8)
        a[:, :, :sampwidth] = raw_bytes.reshape(-1, nchannels, sampwidth)
        a[:, :, sampwidth:] = (a[:, :, sampwidth - 1:sampwidth] >> 7) * 255
        result = a.view('<i4').reshape(a.shape[:-1])
    else:
        # 8 bit samples are stored as unsigned ints; others as signed ints.
        dt_char = 'u' if sampwidth == 1 else 'i'
        a = _np.fromstring(data, dtype='<%s%d' % (dt_char, sampwidth))
        result = a.reshape(-1, nchannels)
    return result


def readwav(file):
    """
    Read a WAV file.

    Parameters
    ----------
    file : string or file object
        Either the name of a file or an open file pointer.

    Return Values
    -------------
    rate : float
        The sampling frequency (i.e. frame rate)
    sampwidth : float
        The sample width, in bytes.  E.g. for a 24 bit WAV file,
        sampwidth is 3.
    data : numpy array
        The array containing the data.  The shape of the array is
        (num_samples, num_channels).  num_channels is the number of
        audio channels (1 for mono, 2 for stereo).

    Notes
    -----
    This function uses the `wave` module of the Python standard libary
    to read the WAV file, so it has the same limitations as that library.
    In particular, the function does not read compressed WAV files.

    """
    wav = _wave.open(file)
    rate = wav.getframerate()
    nchannels = wav.getnchannels()
    sampwidth = wav.getsampwidth()
    nframes = wav.getnframes()
    data = wav.readframes(nframes)
    wav.close()
    array = _wav2array(nchannels, sampwidth, data)
    return rate, sampwidth, array



main()