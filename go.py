# Editor: Michael Sikora
# Date: 2017.04.24
# dependecies: findfundfreq.py waveIO.py
#
# command line call requires a filename after
# example: $python go.py LowE.wav

import sys
from time import sleep
from findfundfreq import *
from waveIO import *
import wave as wf
import pyaudio


def main():
	# Listing wav files in prompt will give each ones freq.
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
	
#-----------------------------------------------------------------------------------
def menu():
	print("--------MENU--------")
	print("1. use a wave file of a note")
	print("2. use an audio input device")
	print("5. quit program")
	choice = int(input("Choose Option:"))

	return choice;
def listDevices():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
	return 0
			
def forstreaming():
	# Show the most intense frequency detected (useful for configuration)
	frequencyoutput=True
	freqNow = 1.0
	freqPast = 1.0

	#Set up audio sampler - 
	NUM_SAMPLES = 2048
	SAMPLING_RATE = 48000 #make sure this matches the sampling rate of your mic!
	pa = pyaudio.PyAudio()
	_stream = pa.open(format=pyaudio.paInt16,
					channels=1, rate=SAMPLING_RATE,
					input=True,
					input_device_index = 1,
					frames_per_buffer=NUM_SAMPLES)

	frames = []
	#for i in range(0, int(SAMPLING_RATE/NUM_SAMPLES * TIME)

	while True:
		#MAYBE THIS??? STILL ATTEMPTING TO GET MY LAPTOP MIC WORKING
		data = fromstring(_stream.read(NUM_SAMPLES))
		print (data)
		normal = data / 32768.0
		#frames.append(data)
		
		#while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
		#audio_data  = fromstring(_stream.read(
		#	_stream.get_read_available()), dtype=short)[-NUM_SAMPLES:]
		# Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
		#normalized_data = audio_data / 32768.0
		
		pitchfrequency = findfundfreq(normal, SAMPLING_RATE, False)
		print(pitchfrequency)
	
	_stream.stop_stream()
	_stream.close()
	pa.terminate()
	
	return 0
	
	
main()