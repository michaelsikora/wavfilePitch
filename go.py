# Editor: Michael Sikora
# Date: 2017.04.24
# dependecies: findfundfreq.py waveIO.py
#
# can be used in command line with a list of filenames as such:
# $python go.py LowE.wav A2.wav B3.wav
#
# or can be run as such:
# $python go.py
#
# audio streaming is default to a continuous loop.
# to exit loop press Ctrl-C from terminal
#
# infinite loop can be replaced with commented out code for a time delay while loop.
# this can be found in forstreaming module

import sys
from time import sleep
from findfundfreq import *
from waveIO import *
import wave as wf
import scipy
import scipy.signal as sgl
import pyaudio
#import matplotlib.pyplot as plt


def main():
	# Listing wav files in prompt will give each ones fundamental freq.
	if (len(sys.argv) > 1): 
		for each in sys.argv[1:]:
			#print(sys.argv[each-1])
			print(each)
			filename = each
			forwavefile(filename)
			
		return 0
		
	# STANDARD MENU	
	action = menu()
	
	while(action != 5):
		if (action == 1):
			filename = input("Enter .wav filename of a note:")
			forwavefile(filename)
		elif (action == 2):
			#listDevices()
			forstreaming()
		else:
			print("incorrect response")
		action = menu()
		
	print("Goodbye")	
	return 0
#-----------------------------------------------------------------------------------
def forwavefile(filename):

	#get volume array from wavefile
	rate, sampwidth, array = readwav(filename)
	#print(rate), print(sampwidth)

	# a is raw mono channel data
	a = array.T[0] #get channel 1
	# b is normalized data
	b = [(ele/2**16.)*2 for ele in a] # normalize data to be between -1 and 1

	# HERES WHERE THE MAGIC HAPPENS --> imported from findfundfreq
	# using the vector of volume data that has been normalized to be between
	# -1 and 1 on the y axis, with the x axis as time, the fundamental frequency
	# is determined. The algorithm utilyzes the autocorrelation method to measure
	# the signals power. This pitch detection method is called WELCH'S METHOD
	
	# argv is normalized data array, sampling rate, and boole for showing graphs
	pitchfrequency = findfundfreq(b, rate, False)
		# SHAZAMMM!!
	
	print(pitchfrequency) # FUNDAMENTAL FREQUENCY!
	
	return 0
	
def menu():
	'''
	simple menu to handle terminal UI
	'''
	print("--------MENU--------")
	print("1. use a wave file of a note")
	print("2. use an audio input device")
	print("5. quit program")
	choice = int(input("Choose Option:"))

	return choice;
	
def listDevices():
	'''
	Utility for lissting audio devices available
	'''
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
	return 0
	
# I DONT THINK THIS FUNCTION WAS USED:
def quadinter(intensity, which, SAMPLING_RATE, NUM_SAMPLES):
	freqNow = 1
	if which != len(intensity)-1:
		y0,y1,y2 = log(intensity[which-1:which+2:])
		x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
		# find the frequency and output it
		freqPast = freqNow
		freqNow = (which+x1)*SAMPLING_RATE/NUM_SAMPLES
	else:
		freqNow = which*SAMPLING_RATE/NUM_SAMPLES
	return freqNow
	
def forstreaming():
	'''
	the main running program when audio input is selected
	pretty much continues buffering and waits til it collects a sample of bufferdata from audio stream,
	while determining freq. then there is code for handling tuning display
	'''
	#counts sample numbers
	samp = 1
	# set delay to have program run for a set time
	delay = 10
	LIFETIMEDATA = []
	# how often to check for pitch consistent results at 20
	samplePeriod = 20	
	#2048 is good
	NUM_SAMPLES = 2048
	SAMPLING_RATE = 44100 #make sure this matches the sampling rate of your mic!
	pa = pyaudio.PyAudio()
	_stream = pa.open(format=pyaudio.paInt16,
					channels=1, rate=SAMPLING_RATE,
					input=True,
					input_device_index = 1,
					frames_per_buffer=NUM_SAMPLES)

	
	#while (delay > 0): #FOR A SET TIME RUN
	while 1: # for a continuous run
		#reset = checkPluck() # IDEA I HAD BUT DIDNT GET TO
		bufferTime = samplePeriod
		pitchfrequency = []
		print('sample number: ' + str(samp))
		buffer = []
		
		while (bufferTime > 0):
			buffer[1:]
			data = _stream.read(NUM_SAMPLES)
			numpydata = np.fromstring(data, dtype=np.int16)
			buffer.append(numpydata)
			onedarray = np.hstack(buffer)[int(NUM_SAMPLES/2):]
			
			# filtering data
			normal = onedarray / 32768.0
			#w = sgl.hanning(30)
			#filtered = sgl.fftconvolve(normal, w)
			filtered = smooth(normal)
			#yhat = sgl.savgol_filter(normal, 11, 3) # window size 51, polynomial order 3
			#b, a = signal.butter(2, 0.1, analog=False)
			#yhat = sgl.lfilter(b,a,sgl.lfilter(b,a, normal))
			
			if (bufferTime < samplePeriod/2):
				# find pitch frequency
				freq = findfundfreq(filtered, SAMPLING_RATE, False)
				pitchfrequency.append(freq)
		
			bufferTime = bufferTime - 1
		
		NOTE = ''	
		tuning = ''
		howclose = ''
		# the last several freq of the sample seem to be most accurate
		PITCH, count = scipy.stats.mode(pitchfrequency)
		if (count < 2): PITCH = 1
		howclose, NOTE = almostANote(PITCH)
		#print(PITCH)
		if (abs(howclose) < 0.05): 
			tuning = 'In Tune'
			print (NOTE + " : " + tuning + " ! ")
		elif ((howclose < 0) & (howclose > -2)): 
			tuning = 'Sharp'
			print (NOTE + " : " + tuning + " by " + str(howclose) + "cents")
		elif ((howclose > 0) & (howclose < 2)): 
			tuning = 'Flat'
			print (NOTE + " : " + tuning + " by " + str(howclose) + "cents")
		else:
			print( ' ' )
		
		samp = samp + 1 #sample number
		delay = delay - 1
		#LIFETIMEDATA.append(filtered) #For set time mode to graph audio input
		
	#this will graph whole input while program was running
	#this = np.hstack(LIFETIMEDATA)
	#plt.plot(this)
	#plt.show()	
	_stream.stop_stream()
	_stream.close()
	pa.terminate()
	
	return 0
	
def cents(freq,ref):
	"""
	converts a frequency to musical cents which are the equidistant value to 
	a given reference pitch. In TET 100 cents is one half note
	"""
	cents = 1200. * np.log2(ref/freq) / 100
	#cents = (np.log2(freq) - np.log2(440) / np.log2(np.power(2,1./1200)) / 100
	return cents
	
def almostANote(a):
	'''
	given a frequency it compares it to 440 herts to get the distance in notes
	to A4. Then it checks if the note is one of the guitar strings and howclose it is
	'''
	distA = cents(a, 440)
	#print(cents(a, 82.9))
	#if (abs(cents(a, 82.9)) < 2):
	#	return (cents(a, 82.9)), 'E2'
	if (abs(distA - 29) < 1):
		return (distA - 29), 'E2'
	elif (abs(distA - 24) < 1):
		return (distA-24), 'A2'
	elif (abs(distA - 19) < 1):
		return (distA-19), 'D3'
	elif (abs(distA - 14) < 1):
		return (distA-14), 'G3'		
	elif (abs(distA - 10) < 1):
		return (distA-10), 'B3'
	elif (abs(distA - 5) < 1):
		return (distA-5), 'E4'
	return False, ''
	
def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError ("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError ("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError ("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y


main()